from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from models import Order, OrderItem, OrderLog, Product, Supermarket, StockOut, StockIn
import datetime

router = APIRouter()

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    supermarket_id: int
    items: List[OrderItemCreate]
    remark: Optional[str] = None
    discount: Optional[float] = 1.0
    total_amount_override: Optional[float] = None

class OrderStatusUpdate(BaseModel):
    status: int
    remark: Optional[str] = None
    tracking_number: Optional[str] = None
    logistics_company: Optional[str] = None

class ReturnItemRequest(BaseModel):
    item_id: int
    quantity: int

class ReturnOrderRequest(BaseModel):
    items: List[ReturnItemRequest]
    remark: Optional[str] = None

def generate_order_no():
    now = datetime.datetime.now()
    return "ORD" + now.strftime("%Y%m%d%H%M%S")

STATUS_MAP = {
    1: "待确认",
    2: "已确认待配货",
    3: "已配货待发货",
    4: "已发货待付款",
    5: "已付款完成",
    6: "已取消",
    7: "已退款"
}

STOCK_OUT_STATUS_MAP = {
    1: "待确认",
    2: "待配货",
    3: "待发货",
    4: "待付款",
    5: "已完成"
}

@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    total_products = db.query(Product).filter(Product.is_active == 1).count()
    total_customers = db.query(Supermarket).count()
    pending_orders = db.query(Order).filter(Order.status == 1).count()
    low_stock = db.query(Product).filter(Product.stock < 10, Product.is_active == 1).count()
    return {
        "products": total_products,
        "supermarkets": total_customers,
        "pending_orders": pending_orders,
        "low_stock": low_stock
    }

@router.get("/")
def get_orders(
    status: Optional[int] = None,
    supermarket_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if supermarket_id:
        query = query.filter(Order.supermarket_id == supermarket_id)
    if date_from:
        query = query.filter(Order.created_at >= date_from)
    if date_to:
        query = query.filter(Order.created_at <= date_to + " 23:59:59")

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_no": o.order_no,
            "supermarket_name": o.supermarket.name if o.supermarket else None,
            "status": o.status,
            "status_text": STATUS_MAP.get(o.status, "未知"),
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "tracking_number": o.tracking_number,
            "logistics_company": o.logistics_company,
            "remark": o.remark,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else None
        })
    return {"total": total, "items": result}

@router.get("/summary")
def get_orders_summary(
    status: Optional[int] = None,
    supermarket_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(func.count(Order.id), func.sum(Order.total_amount))
    if status:
        query = query.filter(Order.status == status)
    if supermarket_id:
        query = query.filter(Order.supermarket_id == supermarket_id)
    if date_from:
        query = query.filter(Order.created_at >= date_from)
    if date_to:
        query = query.filter(Order.created_at <= date_to + " 23:59:59")
    count, total = query.one()
    return {"count": count or 0, "total": float(total or 0)}

@router.get("/my")
def get_my_orders(request: Request, db: Session = Depends(get_db)):
    from jose import jwt
    from jose.exceptions import JWTError
    SECRET_KEY = "warehouse-secret-key-2024"
    ALGORITHM = "HS256"
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效")
    orders = db.query(Order).filter(
        Order.supermarket_id == customer_id
    ).order_by(Order.created_at.desc()).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_no": o.order_no,
            "status": o.status,
            "status_text": STATUS_MAP.get(o.status, "未知"),
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "tracking_number": o.tracking_number,
            "logistics_company": o.logistics_company,
            "remark": o.remark,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else None
        })
    return result

@router.get("/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    items = []
    for item in order.items:
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else None,
            "product_barcode": item.product.barcode if item.product else None,
            "quantity": item.quantity,
            "returned_quantity": item.returned_quantity or 0,
            "unit_price": float(item.unit_price) if item.unit_price else 0,
            "total_price": float(item.total_price) if item.total_price else 0,
        })
    logs = []
    for log in order.logs:
        logs.append({
            "status_text": STATUS_MAP.get(log.status, "操作"),
            "operator_name": log.operator_name,
            "remark": log.remark,
            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else None
        })
    return {
        "id": order.id,
        "order_no": order.order_no,
        "supermarket_name": order.supermarket.name if order.supermarket else None,
        "status": order.status,
        "status_text": STATUS_MAP.get(order.status, "未知"),
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "tracking_number": order.tracking_number,
        "logistics_company": order.logistics_company,
        "remark": order.remark,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
        "items": items,
        "logs": logs
    }

@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    original_total = sum(item.quantity * item.unit_price for item in data.items)
    total = data.total_amount_override if data.total_amount_override is not None else original_total
    order = Order(
        order_no=generate_order_no(),
        supermarket_id=data.supermarket_id,
        status=1,
        total_amount=total,
        remark=data.remark
    )
    db.add(order)
    db.flush()
    for item in data.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        db.add(order_item)
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock -= item.quantity
        stock_out = StockOut(
            product_id=item.product_id,
            product_name=product.name if product else None,
            product_barcode=product.barcode if product else None,
            product_spec=product.spec if product else None,
            order_id=order.id,
            order_no=order.order_no,
            quantity=item.quantity,
            sell_price=item.unit_price,
            reason="订单出售",
            status="待确认"
        )
        db.add(stock_out)
    log = OrderLog(
        order_id=order.id, status=1,
        operator_type=1, operator_name="管理员", remark="创建订单"
    )
    db.add(log)
    db.commit()
    return {"message": "订单创建成功", "order_no": order.order_no}

@router.put("/{order_id}/status")
def update_order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = data.status
    if data.tracking_number:
        order.tracking_number = data.tracking_number
    if data.logistics_company:
        order.logistics_company = data.logistics_company
    log = OrderLog(
        order_id=order.id, status=data.status,
        operator_type=1, operator_name="管理员", remark=data.remark
    )
    db.add(log)
    new_status = STOCK_OUT_STATUS_MAP.get(data.status)
    if new_status:
        stock_outs = db.query(StockOut).filter(
            StockOut.order_id == order_id,
            StockOut.status.notin_(["已退回", "仅退款"])
        ).all()
        for so in stock_outs:
            so.status = new_status
    db.commit()
    return {"message": "订单状态更新成功"}

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="只有待确认订单可以取消")
    order.status = 6
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
        stock_in = StockIn(
            product_id=item.product_id,
            quantity=item.quantity,
            cost_price=item.unit_price,
            total_amount=float(item.unit_price) * item.quantity,
            source="cancel",
            remark=f"取消退回，订单号：{order.order_no}"
        )
        db.add(stock_in)
        stock_outs = db.query(StockOut).filter(
            StockOut.order_id == order_id,
            StockOut.product_id == item.product_id
        ).all()
        for so in stock_outs:
            so.status = "已退回"
    log = OrderLog(
        order_id=order.id, status=6,
        operator_type=1, operator_name="管理员", remark="取消订单，库存已归还"
    )
    db.add(log)
    db.commit()
    return {"message": "订单已取消，库存已归还"}

@router.delete("/{order_id}/items/{item_id}")
def remove_order_item(order_id: int, item_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="只有待确认订单可以删除商品")
    item = db.query(OrderItem).filter(
        OrderItem.id == item_id, OrderItem.order_id == order_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="订单商品不存在")
    if len(order.items) <= 1:
        raise HTTPException(status_code=400, detail="订单至少保留一件商品，请直接取消订单")
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product:
        product.stock += item.quantity
    stock_in = StockIn(
        product_id=item.product_id,
        quantity=item.quantity,
        cost_price=item.unit_price,
        total_amount=float(item.unit_price) * item.quantity,
        source="cancel",
        remark=f"取消退回，订单号：{order.order_no}"
    )
    db.add(stock_in)
    stock_outs = db.query(StockOut).filter(
        StockOut.order_id == order_id,
        StockOut.product_id == item.product_id
    ).all()
    for so in stock_outs:
        so.status = "已退回"
    product_name = item.product.name if item.product else str(item_id)
    order.total_amount = float(order.total_amount) - float(item.total_price)
    db.delete(item)
    log = OrderLog(
        order_id=order.id, status=order.status,
        operator_type=1, operator_name="管理员",
        remark=f"删除商品：{product_name}，库存已归还"
    )
    db.add(log)
    db.commit()
    return {"message": "商品已删除，库存已归还"}

@router.post("/{order_id}/refund")
def refund_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status < 2:
        raise HTTPException(status_code=400, detail="已确认后才可退款")
    order.status = 7
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
        stock_outs = db.query(StockOut).filter(
            StockOut.order_id == order_id,
            StockOut.product_id == item.product_id,
            StockOut.status.notin_(["已退回", "仅退款"])
        ).all()
        for so in stock_outs:
            so.status = "已退回"
    log = OrderLog(
        order_id=order.id, status=7,
        operator_type=1, operator_name="管理员", remark="退款，库存已归还"
    )
    db.add(log)
    db.commit()
    return {"message": "退款成功，库存已归还"}

@router.post("/{order_id}/return")
def return_order(order_id: int, data: ReturnOrderRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status < 4:
        raise HTTPException(status_code=400, detail="已发货后才可退货")
    returned_names = []
    for r in data.items:
        item = db.query(OrderItem).filter(
            OrderItem.id == r.item_id,
            OrderItem.order_id == order_id
        ).first()
        if not item:
            continue
        already_returned = item.returned_quantity or 0
        can_return = item.quantity - already_returned
        if r.quantity > can_return:
            raise HTTPException(
                status_code=400,
                detail=f"退货数量超过可退数量（最多{can_return}）"
            )
        item.returned_quantity = already_returned + r.quantity
        stock_out = db.query(StockOut).filter(
            StockOut.order_id == order_id,
            StockOut.product_id == item.product_id
        ).first()
        if stock_out:
            stock_out.status = "仅退款"
        returned_names.append(
            f"{item.product.name if item.product else '商品'}x{r.quantity}"
        )
    log = OrderLog(
        order_id=order.id, status=order.status,
        operator_type=1, operator_name="管理员",
        remark=f"退货（仅退款，库存不归还）：{', '.join(returned_names)}。{data.remark or ''}"
    )
    db.add(log)
    db.commit()
    return {"message": "退货登记成功，出库记录已标记仅退款"}

@router.post("/{order_id}/client-cancel")
def client_cancel_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    from jose import jwt
    from jose.exceptions import JWTError
    SECRET_KEY = "warehouse-secret-key-2024"
    ALGORITHM = "HS256"
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效")
    order = db.query(Order).filter(Order.id == order_id, Order.supermarket_id == customer_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="只有待确认订单可以取消")
    order.status = 6
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
        stock_in = StockIn(
            product_id=item.product_id,
            quantity=item.quantity,
            cost_price=item.unit_price,
            total_amount=float(item.unit_price) * item.quantity,
            source="cancel",
            remark=f"客户取消，订单号：{order.order_no}"
        )
        db.add(stock_in)
        stock_outs = db.query(StockOut).filter(
            StockOut.order_id == order_id,
            StockOut.product_id == item.product_id
        ).all()
        for so in stock_outs:
            so.status = "已退回"
    log = OrderLog(
        order_id=order.id, status=6,
        operator_type=2, operator_name="客户", remark="客户取消订单，库存已归还"
    )
    db.add(log)
    db.commit()
    return {"message": "订单已取消"}
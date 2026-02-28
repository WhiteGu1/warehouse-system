from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from models import Order, OrderItem, OrderLog, Product, Supermarket
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

class OrderStatusUpdate(BaseModel):
    status: int
    remark: Optional[str] = None
    tracking_number: Optional[str] = None
    logistics_company: Optional[str] = None

def generate_order_no():
    now = datetime.datetime.now()
    return "ORD" + now.strftime("%Y%m%d%H%M%S")

STATUS_MAP = {
    1: "待确认",
    2: "已确认待配货",
    3: "已配货待发货",
    4: "已发货待付款",
    5: "已付款完成"
}

@router.get("/")
def get_orders(status: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()
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
            "product_name": item.product.name if item.product else None,
            "quantity": item.quantity,
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
    total = sum(item.quantity * item.unit_price for item in data.items)
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
    log = OrderLog(
        order_id=order.id,
        status=1,
        operator_type=1,
        operator_name="管理员",
        remark="创建订单"
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
        order_id=order.id,
        status=data.status,
        operator_type=1,
        operator_name="管理员",
        remark=data.remark
    )
    db.add(log)
    if data.status == 4:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock -= item.quantity
    db.commit()
    return {"message": "订单状态更新成功"}

# 首页统计数据
@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    from models import Product, Supermarket
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
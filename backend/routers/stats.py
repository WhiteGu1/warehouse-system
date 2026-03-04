from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Product, StockIn, Order, OrderItem
from typing import Optional
from datetime import datetime, date

router = APIRouter()

def parse_date_range(start, end):
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d") if start else datetime.combine(date.today(), datetime.min.time())
        end_dt = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if end else datetime.combine(date.today(), datetime.max.time())
    except:
        start_dt = datetime.combine(date.today(), datetime.min.time())
        end_dt = datetime.combine(date.today(), datetime.max.time())
    return start_dt, end_dt

@router.get("/flow")
def get_flow(start: Optional[str] = None, end: Optional[str] = None, db: Session = Depends(get_db)):
    start_dt, end_dt = parse_date_range(start, end)

    # 入库支出：排除"取消退回"，只统计真实进货
    stock_in_records = db.query(StockIn).filter(
        StockIn.created_at >= start_dt,
        StockIn.created_at <= end_dt,
        StockIn.source != 'cancel'
    ).order_by(StockIn.created_at.desc()).all()

    stock_in_list = []
    total_cost = 0
    for r in stock_in_records:
        amount = float(r.total_amount) if r.total_amount else 0
        total_cost += amount
        product = r.product
        stock_in_list.append({
            "time": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            "type": "入库",
            "product_name": product.name if product else "-",
            "quantity": r.quantity,
            "unit_price": float(r.cost_price) if r.cost_price else 0,
            "amount": amount,
            "remark": r.remark or ""
        })

    # 销售收入：已完成订单（status=5），按折扣比例分摊
    completed_orders = db.query(Order).filter(
        Order.status == 5,
        Order.created_at >= start_dt,
        Order.created_at <= end_dt
    ).order_by(Order.created_at.desc()).all()

    sales_list = []
    total_sales = 0
    for o in completed_orders:
        original_total = sum(float(i.total_price or 0) for i in o.items)
        actual_total = float(o.total_amount or 0)
        discount_ratio = (actual_total / original_total) if original_total > 0 else 1.0
        for item in o.items:
            original_amount = float(item.total_price or 0)
            actual_amount = round(original_amount * discount_ratio, 2)
            total_sales += actual_amount
            sales_list.append({
                "time": o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else None,
                "type": "销售",
                "product_name": item.product.name if item.product else "-",
                "quantity": item.quantity,
                "unit_price": round(float(item.unit_price or 0) * discount_ratio, 2),
                "amount": actual_amount,
                "remark": o.order_no or ""
            })

    all_records = sorted(stock_in_list + sales_list, key=lambda x: x["time"] or "", reverse=True)

    return {
        "total_sales": round(total_sales, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(total_sales - total_cost, 2),
        "records": all_records
    }

@router.get("/products")
def get_product_stats(start: Optional[str] = None, end: Optional[str] = None, db: Session = Depends(get_db)):
    start_dt, end_dt = parse_date_range(start, end)

    products = db.query(Product).filter(Product.is_active == 1).all()
    result = []

    for p in products:
        # 入库：排除"取消退回"
        stock_ins = db.query(StockIn).filter(
            StockIn.product_id == p.id,
            StockIn.created_at >= start_dt,
            StockIn.created_at <= end_dt,
            StockIn.source != 'cancel'
        ).all()
        total_in_qty = sum(r.quantity for r in stock_ins)
        total_in_cost = sum(float(r.total_amount or 0) for r in stock_ins)
        last_in = max((r.created_at for r in stock_ins), default=None)

        # 销售：已完成订单，批量查询避免 N+1
        order_items = db.query(OrderItem).join(Order).filter(
            OrderItem.product_id == p.id,
            Order.status == 5,
            Order.created_at >= start_dt,
            Order.created_at <= end_dt
        ).all()

        total_out_qty = sum(i.quantity for i in order_items)
        total_out_sales = 0
        last_out_dt = None

        if order_items:
            order_ids = list(set(i.order_id for i in order_items))
            orders_map = {o.id: o for o in db.query(Order).filter(Order.id.in_(order_ids)).all()}
            for i in order_items:
                o = orders_map.get(i.order_id)
                if not o:
                    continue
                original_total = sum(float(x.total_price or 0) for x in o.items)
                actual_total = float(o.total_amount or 0)
                discount_ratio = (actual_total / original_total) if original_total > 0 else 1.0
                total_out_sales += float(i.total_price or 0) * discount_ratio
                if last_out_dt is None or o.created_at > last_out_dt:
                    last_out_dt = o.created_at

        if total_in_qty == 0 and total_out_qty == 0:
            continue

        result.append({
            "id": p.id,
            "name": p.name,
            "spec": p.spec,
            "barcode": p.barcode,
            "image": p.image,
            "stock": p.stock,
            "total_in_qty": total_in_qty,
            "total_in_cost": round(total_in_cost, 2),
            "total_out_qty": total_out_qty,
            "total_out_sales": round(total_out_sales, 2),
            "profit": round(total_out_sales - total_in_cost, 2),
            "last_in": last_in.strftime("%Y-%m-%d %H:%M") if last_in else None,
            "last_out": last_out_dt.strftime("%Y-%m-%d %H:%M") if last_out_dt else None,
        })

    result.sort(key=lambda x: x["total_out_sales"], reverse=True)
    return result
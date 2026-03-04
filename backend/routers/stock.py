from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import StockIn, Product

router = APIRouter()

class StockInCreate(BaseModel):
    product_id: int
    quantity: int
    cost_price: Optional[float] = None
    remark: Optional[str] = None

@router.get("/")
def get_stock_in(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    records = db.query(StockIn).order_by(StockIn.created_at.desc()).all()
    result = []
    for r in records:
        product = r.product
        if keyword and product:
            if keyword not in (product.name or '') and keyword not in (product.barcode or ''):
                continue
        result.append({
            "id": r.id,
            "product_id": r.product_id,
            "product_name": product.name if product else None,
            "product_barcode": product.barcode if product else None,
            "product_spec": product.spec if product else None,
            "quantity": r.quantity,
            "cost_price": float(r.cost_price) if r.cost_price else None,
            "total_amount": float(r.total_amount) if r.total_amount else None,
            "source": r.source,
            "remark": r.remark,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None
        })
    return result

@router.post("/")
def create_stock_in(data: StockInCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 判断是否曾经有过真实入库记录，而不是靠当前库存判断
    existing = db.query(StockIn).filter(
        StockIn.product_id == data.product_id,
        StockIn.source.in_(["manual_new", "manual_add", "import"])
    ).first()

    total = (data.cost_price or 0) * data.quantity
    record = StockIn(
        product_id=data.product_id,
        quantity=data.quantity,
        cost_price=data.cost_price,
        total_amount=total,
        source="manual_new" if not existing else "manual_add",
        remark=data.remark
    )
    db.add(record)
    product.stock += data.quantity
    db.commit()
    return {"message": "入库成功", "new_stock": product.stock}
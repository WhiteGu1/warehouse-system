from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import StockOut

router = APIRouter()

@router.get("/")
def get_stock_out(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    records = db.query(StockOut).order_by(StockOut.created_at.desc()).all()
    result = []
    for r in records:
        if keyword:
            if keyword not in (r.product_name or '') and keyword not in (r.product_barcode or ''):
                continue
        result.append({
            "id": r.id,
            "product_name": r.product_name,
            "product_barcode": r.product_barcode,
            "product_spec": r.product_spec,
            "order_no": r.order_no,
            "quantity": r.quantity,
            "sell_price": float(r.sell_price) if r.sell_price else None,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None
        })
    return result
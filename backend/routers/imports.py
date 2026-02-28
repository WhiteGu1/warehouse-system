from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Product, ImportBatch, ImportFailed, ImportPendingPrice, Category
import openpyxl
import io
import json

router = APIRouter()

def to_int_col(val):
    try:
        return int(val)
    except:
        return None

@router.get("/batches")
def get_batches(db: Session = Depends(get_db)):
    batches = db.query(ImportBatch).order_by(ImportBatch.created_at.desc()).all()
    return [{
        "id": b.id,
        "batch_name": b.batch_name,
        "total": b.total,
        "success": b.success,
        "failed": b.failed,
        "pending_price": b.pending_price,
        "created_at": b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else None
    } for b in batches]

@router.post("/upload")
async def import_excel(file: UploadFile = File(...), column_map: str = "", db: Session = Depends(get_db)):
    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.worksheets[0]

    try:
        col_map = json.loads(column_map) if column_map else {}
    except:
        col_map = {}

    name_col = to_int_col(col_map.get("name"))
    cost_col = to_int_col(col_map.get("cost_price"))
    sell_col = to_int_col(col_map.get("sell_price"))
    stock_col = to_int_col(col_map.get("stock"))
    spec_col = to_int_col(col_map.get("spec"))
    barcode_col = to_int_col(col_map.get("barcode"))
    remark_col = to_int_col(col_map.get("remark"))

    uncategorized = db.query(Category).filter(Category.name == "未分类").first()
    uncategorized_id = uncategorized.id if uncategorized else None

    batch = ImportBatch(batch_name=file.filename)
    db.add(batch)
    db.flush()

    success = 0
    failed = 0
    pending_price = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        row = list(row)

        def get_col(col_index):
            if col_index is None:
                return None
            try:
                return row[int(col_index)]
            except:
                return None

        name = get_col(name_col)
        cost_price = get_col(cost_col)
        sell_price = get_col(sell_col)
        stock = get_col(stock_col)
        spec = get_col(spec_col)
        barcode = get_col(barcode_col)
        remark = get_col(remark_col)

        if not any(row):
            continue

        row_summary = f"名称:{name} 进价:{cost_price} 数量:{stock}"

        if not name:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason="商品名称为空"))
            continue

        if cost_price is None or str(cost_price).strip() == '':
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"{name} - 进价错误：进价为空"))
            continue

        try:
            cost_price_float = float(str(cost_price))
        except:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"{name} - 进价错误：必须为纯数字，当前值：{cost_price}"))
            continue

        try:
            stock_int = int(float(str(stock)))
            if stock_int == 0:
                raise ValueError("数量为0")
        except:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"{name} - 数量错误：必须为纯数字且不为0，当前值：{stock}"))
            continue

        sell_price_float = None
        if sell_price is not None and str(sell_price).strip() != '':
            try:
                sell_price_float = float(str(sell_price))
            except:
                failed += 1
                db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"{name} - 售价错误：必须为纯数字，当前值：{sell_price}"))
                continue

        product = Product(
            name=str(name),
            cost_price=cost_price_float,
            sell_price=sell_price_float,
            stock=stock_int,
            spec=str(spec) if spec else None,
            barcode=str(barcode) if barcode else None,
            remark=str(remark) if remark else None,
            category_id=uncategorized_id,
            is_active=1
        )
        db.add(product)
        db.flush()

        if not sell_price_float:
            pending_price += 1
            db.add(ImportPendingPrice(batch_id=batch.id, product_id=product.id))

        success += 1

    batch.total = success + failed
    batch.success = success
    batch.failed = failed
    batch.pending_price = pending_price

    db.commit()
    return {
        "message": f"导入完成：成功{success}条，失败{failed}条，待确认价格{pending_price}条",
        "batch_id": batch.id,
        "success": success,
        "failed": failed,
        "pending_price": pending_price
    }

@router.delete("/batches/{batch_id}")
def rollback_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    pending = db.query(ImportPendingPrice).filter(ImportPendingPrice.batch_id == batch_id).all()
    pending_ids = [p.product_id for p in pending]

    db.query(ImportPendingPrice).filter(ImportPendingPrice.batch_id == batch_id).delete()
    db.query(ImportFailed).filter(ImportFailed.batch_id == batch_id).delete()

    for pid in pending_ids:
        product = db.query(Product).filter(Product.id == pid).first()
        if product:
            db.delete(product)

    db.delete(batch)
    db.commit()
    return {"message": "批次已撤回"}

@router.get("/failed/{batch_id}")
def get_failed(batch_id: int, db: Session = Depends(get_db)):
    records = db.query(ImportFailed).filter(ImportFailed.batch_id == batch_id).all()
    return [{"id": r.id, "row_data": r.row_data, "reason": r.reason} for r in records]

@router.delete("/failed/{batch_id}")
def clear_failed(batch_id: int, db: Session = Depends(get_db)):
    db.query(ImportFailed).filter(ImportFailed.batch_id == batch_id).delete()
    db.commit()
    return {"message": "失败记录已清空"}

@router.get("/pending-price")
def get_pending_price(db: Session = Depends(get_db)):
    records = db.query(ImportPendingPrice).filter(ImportPendingPrice.confirmed == 0).all()
    return [{
        "id": r.id,
        "product_id": r.product_id,
        "product_name": r.product.name if r.product else None,
        "cost_price": float(r.product.cost_price) if r.product and r.product.cost_price else None,
        "sell_price": float(r.product.sell_price) if r.product and r.product.sell_price else None,
        "spec": r.product.spec if r.product else None,
    } for r in records]

@router.put("/pending-price/{record_id}")
def confirm_price(record_id: int, data: dict, db: Session = Depends(get_db)):
    record = db.query(ImportPendingPrice).filter(ImportPendingPrice.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    product = db.query(Product).filter(Product.id == record.product_id).first()
    if product:
        product.sell_price = data.get("sell_price")
    record.confirmed = 1
    db.commit()
    return {"message": "价格已确认"}
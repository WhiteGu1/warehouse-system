from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Product, ImportBatch, ImportFailed, ImportPendingPrice, Category, StockIn
import openpyxl
import io
import json
import uuid
import os
import requests as req_lib
from PIL import Image as PilImage

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def to_int_col(val):
    try:
        return int(val)
    except:
        return None

def crop_and_save_image(url: str):
    try:
        resp = req_lib.get(url.strip(), timeout=5)
        if resp.status_code != 200:
            return None
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        img = PilImage.open(io.BytesIO(resp.content)).convert("RGB")
        w, h = img.size
        target_ratio = 4 / 3
        if (w / h) > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        img.save(filepath, "JPEG")
        return f"/uploads/{filename}"
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
async def import_excel(file: UploadFile = File(...), column_map: str = Form(""), db: Session = Depends(get_db)):
    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
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
    middle_pack_col = to_int_col(col_map.get("middle_pack"))
    piece_col = to_int_col(col_map.get("piece"))
    image_col = to_int_col(col_map.get("image_col"))

    # 提取嵌入图片，按行号建立映射
    image_map = {}
    try:
        for img in ws._images:
            row_num = img.anchor._from.row + 1
            img_data = img._data()
            filename = f"{uuid.uuid4()}.jpg"
            filepath = os.path.join(UPLOAD_DIR, filename)
            pil_img = PilImage.open(io.BytesIO(img_data)).convert("RGB")
            w, h = pil_img.size
            target_ratio = 4 / 3
            if (w / h) > target_ratio:
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                pil_img = pil_img.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / target_ratio)
                top = (h - new_h) // 2
                pil_img = pil_img.crop((0, top, w, top + new_h))
            pil_img.save(filepath, "JPEG")
            image_map[row_num] = f"/uploads/{filename}"
    except:
        pass

    uncategorized = db.query(Category).filter(Category.name == "未分类").first()
    uncategorized_id = uncategorized.id if uncategorized else None

    batch = ImportBatch(batch_name=file.filename)
    db.add(batch)
    db.flush()

    success = 0
    failed = 0
    pending_price = 0

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
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
        middle_pack = get_col(middle_pack_col)
        piece = get_col(piece_col)
        image_url = get_col(image_col)

        if not any(row):
            continue

        row_parts = [f"第{row_idx}行", f"名称:{name}", f"进价:{cost_price}", f"数量:{stock}"]
        if sell_price: row_parts.append(f"售价:{sell_price}")
        if spec: row_parts.append(f"规格:{spec}")
        if barcode: row_parts.append(f"条码:{barcode}")
        if remark: row_parts.append(f"备注:{remark}")
        row_summary = " | ".join(row_parts)

        if not name:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 - 商品名称为空"))
            continue

        if cost_price is None or str(cost_price).strip() == '':
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 {name} - 进价为空"))
            continue

        try:
            cost_price_float = float(str(cost_price))
        except:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 {name} - 进价必须为纯数字，当前值：{cost_price}"))
            continue

        try:
            stock_int = int(float(str(stock)))
            if stock_int == 0:
                raise ValueError("数量为0")
        except:
            failed += 1
            db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 {name} - 数量错误：必须为纯数字且不为0，当前值：{stock}"))
            continue

        sell_price_float = None
        if sell_price is not None and str(sell_price).strip() != '':
            try:
                sell_price_float = float(str(sell_price))
            except:
                failed += 1
                db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 {name} - 售价必须为纯数字，当前值：{sell_price}"))
                continue

        if barcode:
            existing = db.query(Product).filter(Product.barcode == str(barcode)).first()
            if existing:
                failed += 1
                db.add(ImportFailed(batch_id=batch.id, row_data=row_summary[:500], reason=f"第{row_idx}行 {name} - 条码重复：{barcode}"))
                continue

        middle_pack_int = None
        if middle_pack is not None:
            try:
                middle_pack_int = int(float(str(middle_pack)))
            except:
                pass

        piece_int = None
        if piece is not None:
            try:
                piece_int = int(float(str(piece)))
            except:
                pass

        product = Product(
            name=str(name),
            cost_price=cost_price_float,
            sell_price=sell_price_float,
            stock=stock_int,
            spec=str(spec) if spec else None,
            barcode=str(barcode) if barcode else None,
            remark=str(remark) if remark else None,
            middle_pack=middle_pack_int,
            piece=piece_int,
            category_id=uncategorized_id,
            is_active=1
        )
        db.add(product)
        db.flush()

        # 入库记录
        stock_record = StockIn(
            product_id=product.id,
            quantity=stock_int,
            cost_price=cost_price_float,
            total_amount=cost_price_float * stock_int,
            source="import",
            remark="Excel导入"
        )
        db.add(stock_record)

        # 图片处理：优先嵌入图片，其次URL
        if row_idx in image_map:
            product.image = image_map[row_idx]
        elif image_url and str(image_url).strip():
            saved_path = crop_and_save_image(str(image_url).strip())
            if saved_path:
                product.image = saved_path

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

@router.delete("/pending-price/{record_id}")
def delete_pending_price(record_id: int, db: Session = Depends(get_db)):
    record = db.query(ImportPendingPrice).filter(ImportPendingPrice.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "已删除"}
@router.delete("/failed-single/{record_id}")
def delete_failed_single(record_id: int, db: Session = Depends(get_db)):
    record = db.query(ImportFailed).filter(ImportFailed.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "已删除"}
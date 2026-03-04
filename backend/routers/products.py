from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Product, Category, StockIn, StockOut
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ProductCreate(BaseModel):
    barcode: Optional[str] = None
    name: str
    category_id: Optional[int] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None
    stock: Optional[int] = 0
    remark: Optional[str] = None
    middle_pack: Optional[int] = 1
    piece: Optional[int] = None
    item_no: Optional[str] = None

class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    name: Optional[str] = None
    category_id: Optional[int] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None
    remark: Optional[str] = None
    middle_pack: Optional[int] = None
    piece: Optional[int] = None
    item_no: Optional[str] = None

class StockInAdd(BaseModel):
    quantity: int
    cost_price: Optional[float] = None
    remark: Optional[str] = None

@router.get("/")
def get_products(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == 1)
    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) | (Product.barcode.contains(keyword))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    products = query.all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "barcode": p.barcode,
            "name": p.name,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "spec": p.spec,
            "unit": p.unit,
            "cost_price": float(p.cost_price) if p.cost_price else None,
            "sell_price": float(p.sell_price) if p.sell_price else None,
            "stock": p.stock,
            "image": p.image,
            "remark": p.remark,
            "middle_pack": p.middle_pack,
            "piece": p.piece,
            "item_no": p.item_no,
        })
    return result

@router.get("/{product_id}/stock-history")
def get_stock_history(product_id: int, db: Session = Depends(get_db)):
    records = db.query(StockIn).filter(StockIn.product_id == product_id).order_by(StockIn.created_at.desc()).all()
    return [{
        "id": r.id,
        "quantity": r.quantity,
        "cost_price": float(r.cost_price) if r.cost_price else None,
        "total_amount": float(r.total_amount) if r.total_amount else None,
        "source": r.source,
        "remark": r.remark,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None
    } for r in records]

@router.post("/")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.barcode:
        existing = db.query(Product).filter(Product.barcode == data.barcode).first()
        if existing:
            raise HTTPException(status_code=400, detail="条形码已存在")
    product_data = data.model_dump()
    init_stock = product_data.pop("stock", 0) or 0
    product_data["stock"] = 0
    product = Product(**product_data)
    db.add(product)
    db.flush()
    if init_stock > 0:
        record = StockIn(
            product_id=product.id,
            quantity=init_stock,
            cost_price=data.cost_price,
            total_amount=(data.cost_price or 0) * init_stock,
            source="manual_new",
            remark="新增商品"
        )
        db.add(record)
        product.stock = init_stock
    db.commit()
    return {"message": "商品添加成功", "id": product.id}

@router.post("/{product_id}/stockin")
def stockin_product(product_id: int, data: StockInAdd, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    record = StockIn(
        product_id=product_id,
        quantity=data.quantity,
        cost_price=data.cost_price,
        total_amount=(data.cost_price or 0) * data.quantity,
        source="manual_add",
        remark=data.remark
    )
    db.add(record)
    product.stock += data.quantity
    db.commit()
    return {"message": "入库成功", "new_stock": product.stock}

@router.post("/{product_id}/image")
async def upload_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    product.image = f"/uploads/{filename}"
    db.commit()
    return {"image": product.image}

@router.put("/{product_id}")
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    return {"message": "商品更新成功"}

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.stock and product.stock > 0:
        stock_out = StockOut(
            product_id=product.id,
            product_name=product.name,
            product_barcode=product.barcode,
            product_spec=product.spec,
            order_id=None,
            order_no=None,
            quantity=product.stock,
            sell_price=None,
            reason="商品删除",
            status="deleted"
        )
        db.add(stock_out)
    product.is_active = 0
    db.commit()
    return {"message": "商品删除成功"}

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name} for c in categories]
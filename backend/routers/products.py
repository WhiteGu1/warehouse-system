from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Product, Category

router = APIRouter()

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

class ProductUpdate(ProductCreate):
    pass

# 获取商品列表
@router.get("/")
def get_products(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == 1)
    if keyword:
        query = query.filter(Product.name.contains(keyword))
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
            "remark": p.remark,
        })
    return result

# 新增商品
@router.post("/")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.barcode:
        existing = db.query(Product).filter(Product.barcode == data.barcode).first()
        if existing:
            raise HTTPException(status_code=400, detail="条形码已存在")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "商品添加成功", "id": product.id}

# 编辑商品
@router.put("/{product_id}")
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    return {"message": "商品更新成功"}

# 删除商品（软删除）
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.is_active = 0
    db.commit()
    return {"message": "商品删除成功"}

# 获取所有分类
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name} for c in categories]
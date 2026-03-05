from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Category, Product

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str
    name_es: Optional[str] = None

@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    result = []
    for c in categories:
        count = db.query(Product).filter(Product.category_id == c.id, Product.is_active == 1).count()
        result.append({"id": c.id, "name": c.name, "name_es": c.name_es, "product_count": count})
    return result

@router.post("/")
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    category = Category(name=data.name, name_es=data.name_es)
    db.add(category)
    db.commit()
    return {"message": "分类创建成功"}

@router.put("/{category_id}")
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    category.name = data.name
    category.name_es = data.name_es
    db.commit()
    return {"message": "分类更新成功"}

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    count = db.query(Product).filter(Product.category_id == category_id, Product.is_active == 1).count()
    if count > 0:
        raise HTTPException(status_code=400, detail=f"该分类下有{count}个商品，无法删除")
    db.delete(category)
    db.commit()
    return {"message": "分类删除成功"}
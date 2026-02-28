from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Supermarket
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CustomerCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    username: str
    password: str

class CustomerUpdate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[int] = 1

# 获取客户列表
@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Supermarket).all()
    result = []
    for c in customers:
        result.append({
            "id": c.id,
            "name": c.name,
            "contact_person": c.contact_person,
            "phone": c.phone,
            "address": c.address,
            "username": c.username,
            "is_active": c.is_active,
            "created_at": c.created_at.strftime("%Y-%m-%d") if c.created_at else None
        })
    return result

# 新增客户
@router.post("/")
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Supermarket).filter(Supermarket.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    customer = Supermarket(
        name=data.name,
        contact_person=data.contact_person,
        phone=data.phone,
        address=data.address,
        username=data.username,
        password=pwd_context.hash(data.password)
    )
    db.add(customer)
    db.commit()
    return {"message": "客户添加成功"}

# 编辑客户
@router.put("/{customer_id}")
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Supermarket).filter(Supermarket.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    customer.name = data.name
    customer.contact_person = data.contact_person
    customer.phone = data.phone
    customer.address = data.address
    customer.is_active = data.is_active
    db.commit()
    return {"message": "客户更新成功"}

# 重置密码
@router.put("/{customer_id}/reset-password")
def reset_password(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Supermarket).filter(Supermarket.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    customer.password = pwd_context.hash("123456")
    db.commit()
    return {"message": "密码已重置为123456"}
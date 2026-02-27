from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Admin, Supermarket
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "warehouse-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class LoginRequest(BaseModel):
    username: str
    password: str

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/admin/login")
def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    if not admin or not pwd_context.verify(request.password, admin.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token({"sub": str(admin.id), "role": "admin"})
    return {"token": token, "name": admin.name, "role": "admin"}

@router.post("/supermarket/login")
def supermarket_login(request: LoginRequest, db: Session = Depends(get_db)):
    market = db.query(Supermarket).filter(Supermarket.username == request.username).first()
    if not market or not pwd_context.verify(request.password, market.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not market.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_token({"sub": str(market.id), "role": "supermarket"})
    return {"token": token, "name": market.name, "role": "supermarket"}
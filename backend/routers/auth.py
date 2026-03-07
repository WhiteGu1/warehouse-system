from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Admin, Supermarket
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

SECRET_KEY = "xK9#mP2$vL8@n”5&wR3!jT6^uY+*o《4!hG7@dF0$bN5^cM2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/admin/login")
@limiter.limit("10/minute")
def admin_login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not pwd_context.verify(data.password, admin.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token({"sub": str(admin.id), "role": "admin"})
    return {"token": token, "name": admin.name, "role": "admin"}

@router.post("/supermarket/login")
@limiter.limit("10/minute")
def supermarket_login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    market = db.query(Supermarket).filter(Supermarket.username == data.username).first()
    if not market or not pwd_context.verify(data.password, market.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not market.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_token({"sub": str(market.id), "role": "supermarket"})
    return {"token": token, "name": market.name, "role": "supermarket"}

@router.post("/client-login")
@limiter.limit("10/minute")
def client_login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    customer = db.query(Supermarket).filter(Supermarket.username == data.username).first()
    if not customer or not pwd_context.verify(data.password, customer.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if not customer.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_token({"sub": str(customer.id), "role": "supermarket"})
    return {
        "access_token": token,
        "user": {
            "id": customer.id,
            "name": customer.contact_person or customer.username,
            "username": customer.username,
            "discount": float(customer.discount) if customer.discount else 1.0
        }
    }

@router.post("/client-change-password")
def client_change_password(data: ChangePasswordRequest, request: Request, db: Session = Depends(get_db)):
    from jose.exceptions import JWTError
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效")
    customer = db.query(Supermarket).filter(Supermarket.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not pwd_context.verify(data.old_password, customer.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    customer.password = pwd_context.hash(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}
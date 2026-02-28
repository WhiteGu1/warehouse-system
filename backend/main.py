from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth, products, stock, customers

# 自动创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="出入库管理系统", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["登录"])
app.include_router(products.router, prefix="/api/products", tags=["商品管理"])
app.include_router(stock.router, prefix="/api/stock", tags=["入库管理"])
app.include_router(customers.router, prefix="/api/customers", tags=["客户管理"])

@app.get("/")
def root():
    return {"message": "服务器运行正常"}
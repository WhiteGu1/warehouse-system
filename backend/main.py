from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import engine
import models
import os
from routers import auth, products, stock, customers, orders, imports, stock_out, categories, stats

models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="出入库管理系统", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["登录"])
app.include_router(products.router, prefix="/api/products", tags=["商品管理"])
app.include_router(stock.router, prefix="/api/stock", tags=["入库记录"])
app.include_router(stock_out.router, prefix="/api/stock-out", tags=["出库记录"])
app.include_router(customers.router, prefix="/api/customers", tags=["客户管理"])
app.include_router(orders.router, prefix="/api/orders", tags=["订单管理"])
app.include_router(imports.router, prefix="/api/imports", tags=["Excel导入"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类管理"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计分析"])

@app.get("/")
def root():
    return {"message": "服务器运行正常"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth

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

@app.get("/")
def root():
    return {"message": "服务器运行正常"}
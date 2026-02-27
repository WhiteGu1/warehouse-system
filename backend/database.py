from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
# 格式: mysql+pymysql://用户名:密码@地址:端口/数据库名
DATABASE_URL = "mysql+pymysql://root:admin123@localhost:3306/warehouse?charset=utf8mb4"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 获取数据库连接（每个请求用完自动关闭）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
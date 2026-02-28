from sqlalchemy import Column, Integer, String, Numeric, SmallInteger, TEXT, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(50))
    created_at = Column(DateTime, default=func.now())

class Supermarket(Base):
    __tablename__ = "supermarkets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(50))
    phone = Column(String(30))
    address = Column(String(200))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    spec = Column(String(100))
    unit = Column(String(20))
    cost_price = Column(Numeric(10, 2))
    sell_price = Column(Numeric(10, 2))
    stock = Column(Integer, default=0)
    image = Column(String(255))
    remark = Column(TEXT)
    is_active = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())
    category = relationship("Category")

class StockIn(Base):
    __tablename__ = "stock_in"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost_price = Column(Numeric(10, 2))
    total_amount = Column(Numeric(10, 2))
    admin_id = Column(Integer, ForeignKey("admins.id"))
    remark = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    status = Column(SmallInteger, default=1)
    total_amount = Column(Numeric(10, 2))
    tracking_number = Column(String(100))
    logistics_company = Column(String(100))
    remark = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    supermarket = relationship("Supermarket")
    items = relationship("OrderItem", back_populates="order")
    logs = relationship("OrderLog", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class OrderLog(Base):
    __tablename__ = "order_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(SmallInteger)
    operator_type = Column(SmallInteger)
    operator_id = Column(Integer)
    operator_name = Column(String(50))
    remark = Column(TEXT)
    created_at = Column(DateTime, default=func.now())
    order = relationship("Order", back_populates="logs")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Numeric(10, 2))
    payment_method = Column(String(50))
    payment_date = Column(DateTime)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    remark = Column(TEXT)
    created_at = Column(DateTime, default=func.now())

class ImportBatch(Base):
    __tablename__ = "import_batches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_name = Column(String(100))
    total = Column(Integer, default=0)
    success = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    pending_price = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

class ImportFailed(Base):
    __tablename__ = "import_failed"
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"))
    row_data = Column(String(500))
    reason = Column(String(200))
    created_at = Column(DateTime, default=func.now())

class ImportPendingPrice(Base):
    __tablename__ = "import_pending_price"
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    confirmed = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=func.now())
    product = relationship("Product")
-- 出入库管理系统数据库设计
-- 适用：小商品供应商管理多家超市

CREATE DATABASE warehouse DEFAULT CHARACTER SET utf8mb4;
USE warehouse;

-- 1. 管理员表
CREATE TABLE admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 超市账号表
CREATE TABLE supermarkets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(50),
    phone VARCHAR(30),
    address VARCHAR(200),
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_active TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 商品分类表
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL
);

-- 预设分类
INSERT INTO categories (name) VALUES
('杂货'),('首饰'),('化妆品'),('玩具'),('餐具'),('五金'),('手机配件');

-- 4. 商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    category_id INT,
    spec VARCHAR(100),
    unit VARCHAR(20),
    cost_price DECIMAL(10,2),
    sell_price DECIMAL(10,2),
    stock INT DEFAULT 0,
    image VARCHAR(255),
    remark TEXT,
    is_active TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 5. 入库记录表
CREATE TABLE stock_in (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    cost_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    admin_id INT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

-- 6. 订单表
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    supermarket_id INT NOT NULL,
    status TINYINT DEFAULT 1 COMMENT '1待确认 2已确认待配货 3已配货待发货 4已发货待付款 5已付款完成',
    total_amount DECIMAL(10,2),
    tracking_number VARCHAR(100),
    logistics_company VARCHAR(100),
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supermarket_id) REFERENCES supermarkets(id)
);

-- 7. 订单明细表
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 8. 订单操作记录表（记录每次状态变更详情）
CREATE TABLE order_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    status TINYINT,
    operator_type TINYINT COMMENT '1管理员 2超市',
    operator_id INT,
    operator_name VARCHAR(50),
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- 9. 付款记录表
CREATE TABLE payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    payment_date DATETIME,
    admin_id INT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);
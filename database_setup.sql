-- ========================================
-- RetailManV2 Database Setup Script (Optimized)
-- ========================================

-- Create Database (with charset for proper encoding)
CREATE DATABASE IF NOT EXISTS retail_man_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE retail_man_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ========================================
-- 1. USERS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255),
    role ENUM('admin', 'staff') DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_users_phone (phone)
) ENGINE=InnoDB;

-- ========================================
-- 2. PRODUCTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_products_name (name)
) ENGINE=InnoDB;

-- ========================================
-- 3. STOCK TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    imei VARCHAR(15) NOT NULL,
    colour VARCHAR(100),
    quantity INT DEFAULT 1,
    batch_no VARCHAR(50),
    added_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_stock_imei (imei),
    INDEX idx_stock_product (product_id),
    INDEX idx_stock_added_by (added_by),

    CONSTRAINT fk_stock_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_stock_user FOREIGN KEY (added_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- 4. PLAZA TABLE (Sales)
-- ========================================
CREATE TABLE IF NOT EXISTS plaza (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    imei VARCHAR(15) NOT NULL,
    colour VARCHAR(100),
    quantity INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    recorded_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_plaza_product (product_id),
    INDEX idx_plaza_customer_phone (customer_phone),

    CONSTRAINT fk_plaza_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_plaza_user FOREIGN KEY (recorded_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- 5. RETURNS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plaza_id INT NOT NULL,
    imei VARCHAR(15) NOT NULL,
    product_id INT NOT NULL,
    colour VARCHAR(100),
    quantity INT NOT NULL,
    reason TEXT,
    recorded_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_returns_plaza (plaza_id),
    INDEX idx_returns_product (product_id),

    CONSTRAINT fk_returns_plaza FOREIGN KEY (plaza_id)
        REFERENCES plaza(id) ON DELETE CASCADE,

    CONSTRAINT fk_returns_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_returns_user FOREIGN KEY (recorded_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- 6. SENDING TABLE (Dispatch)
-- ========================================
CREATE TABLE IF NOT EXISTS sending (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_contact VARCHAR(20) NOT NULL,
    description TEXT,
    sent_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_sending_product (product_id),

    CONSTRAINT fk_sending_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_sending_user FOREIGN KEY (sent_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE collected (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sending_id INT,
    product_id INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_contact VARCHAR(20) NOT NULL,
    description TEXT,
    collected_by_name VARCHAR(255) NOT NULL,
    collected_by_phone VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'collected',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_collected_sending
        FOREIGN KEY (sending_id)
        REFERENCES sending(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_collected_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);
-- ========================================
-- 7. LOGS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_logs_user (user_id),
    INDEX idx_logs_table_record (table_name, record_id),

    CONSTRAINT fk_logs_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;



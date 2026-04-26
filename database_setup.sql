-- ========================================
-- RetailManV2 Database Setup Script (Enterprise)
-- ========================================

CREATE DATABASE IF NOT EXISTS retail_man_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE retail_man_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ========================================
-- 1. USERS
-- ========================================
CREATE TABLE users (
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
-- 2. PRODUCTS
-- ========================================
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_products_name (name)
) ENGINE=InnoDB;


-- ========================================
-- 3. STOCK
-- ========================================
CREATE TABLE stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    imei VARCHAR(20) NOT NULL,
    colour VARCHAR(100),
    quantity INT DEFAULT 1,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 STOCK BATCH

    added_by INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_stock_imei (imei),
    INDEX idx_stock_product (product_id),

    CONSTRAINT fk_stock_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_stock_user FOREIGN KEY (added_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================
-- 4. PLAZA (ENTRY STAGE)
-- ========================================
CREATE TABLE plaza (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 PLAZA ENTRY ID

    product_id INT NOT NULL,
    imei VARCHAR(20) NOT NULL,
    colour VARCHAR(100),
    quantity INT NOT NULL,

    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),

    recorded_by INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_plaza_product (product_id),

    CONSTRAINT fk_plaza_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_plaza_user FOREIGN KEY (recorded_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================
-- 5. PLAZA SALES (FINALIZED SALES)
-- ========================================
CREATE TABLE plaza_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 PLAZA SALE ID (PLAZA_SALE-0001)

    plaza_id INT NOT NULL,
    product_id INT NOT NULL,
    imei VARCHAR(20) NOT NULL,
    colour VARCHAR(100),
    quantity INT NOT NULL,

    sold_by INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_ps_product (product_id),

    CONSTRAINT fk_ps_plaza FOREIGN KEY (plaza_id)
        REFERENCES plaza(id) ON DELETE CASCADE,

    CONSTRAINT fk_ps_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_ps_user FOREIGN KEY (sold_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================
-- 6. PREMISES SALES
-- ========================================
CREATE TABLE premises_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 PREMISES_SALE-0001

    product_id INT,
    imei VARCHAR(50),
    colour VARCHAR(50),
    quantity INT,

    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),

    sold_by INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- ========================================
-- 7. RETURNS
-- ========================================
CREATE TABLE returns (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 RETURN-0001

    plaza_id INT,
    imei VARCHAR(20),
    product_id INT,
    colour VARCHAR(100),
    quantity INT,

    reason TEXT,
    recorded_by INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_returns_product (product_id),

    CONSTRAINT fk_returns_plaza FOREIGN KEY (plaza_id)
        REFERENCES plaza(id) ON DELETE SET NULL,

    CONSTRAINT fk_returns_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_returns_user FOREIGN KEY (recorded_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================
-- 8. SENDING (DISPATCH)
-- ========================================
CREATE TABLE sending (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 SENDING-0001

    product_id INT,
    customer_name VARCHAR(255),
    customer_contact VARCHAR(20),
    description TEXT,

    sent_by INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sending_product FOREIGN KEY (product_id)
        REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_sending_user FOREIGN KEY (sent_by)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================
-- 9. COLLECTED
-- ========================================
CREATE TABLE collected (
    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_no VARCHAR(50) UNIQUE, -- 🔥 COLLECTED-0001

    sending_id INT,
    product_id INT,

    customer_name VARCHAR(255),
    customer_contact VARCHAR(20),

    collected_by_name VARCHAR(255),
    collected_by_phone VARCHAR(20),

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
) ENGINE=InnoDB;


-- ========================================
-- 10. LOGS
-- ========================================
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    action VARCHAR(100),
    table_name VARCHAR(100),
    record_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_logs_user (user_id),

    CONSTRAINT fk_logs_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- 11. BATCH SEQUENCES (CRITICAL)
-- ========================================
CREATE TABLE batch_sequences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module VARCHAR(50) NOT NULL UNIQUE,  -- plaza_sales, returns, sending, etc
    current_value INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

SET FOREIGN_KEY_CHECKS = 1;
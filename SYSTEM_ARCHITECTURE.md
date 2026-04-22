# RetailMan V2.0.1 - System Architecture & Services Verification

## 🏗️ System Architecture

### Roles & Permissions
- **ADMIN**: Full access to all features including Logs, Users, Products
- **STAFF**: Access to core operations (Stock, Plaza, Sending, Returns, Dashboard)

### Dashboard by Role
```
ADMIN DASHBOARD:
├─ 🏠 Dashboard (KPI Cards + Alerts)
├─ 📦 Stock (Add/View inventory)
├─ 🚚 Sending (Dispatch management)
├─ 🛍️  Plaza (Sales records)
├─ ↩️  Returns (Return tracking)
├─ 📊 Logs (Audit trail) [ADMIN ONLY]
├─ 👥 Users (User management) [ADMIN ONLY]
├─ 📋 Products (Product catalog) [ADMIN ONLY]
└─ 🔓 Logout

STAFF DASHBOARD:
├─ 🏠 Dashboard (KPI Cards + Alerts)
├─ 📦 Stock (Add/View inventory)
├─ 🚚 Sending (Dispatch management)
├─ 🛍️  Plaza (Sales records)
├─ ↩️  Returns (Return tracking)
└─ 🔓 Logout
```

---

## 📦 Services Overview

### 1. **StockService** (`services/stock_service.py`)
**Purpose**: Manage inventory and stock operations

**Key Methods**:
- `add_stock(user_id, product_id, imei, colour, quantity)` 
  - Validates IMEI (15 chars, unique)
  - Creates stock record
  - Logs action

- `get_aggregated_stock()`
  - Returns stock grouped by product_id and colour
  - Calculates total_quantity per color
  - Used for dashboard KPI cards

**Access**: STAFF & ADMIN

**Database Table**: `stock`
- Columns: id, product_id, imei, colour, quantity, added_by, created_at

---

### 2. **PlazaService** (`services/plaza_services.py`)
**Purpose**: Record sales transactions

**Key Methods**:
- `record_sale(user_id, product_id, imei, quantity, customer_name, customer_phone)`
  - Validates all fields
  - Checks IMEI exists in stock
  - Creates plaza (sale) record
  - Logs action

- `get_all()` - Returns all sales records

- `get_sales_by_staff()` - Aggregates sales by staff member

**Access**: STAFF & ADMIN

**Database Table**: `plaza`
- Columns: id, customer_name, customer_phone, product_id, imei, quantity, recorded_by, created_at

---

### 3. **SendingService** (`services/sending_services.py`)
**Purpose**: Manage product dispatches/shipments

**Key Methods**:
- `create_dispatch(user_id, product_id, quantity, customer_contact, description)`
  - Validates product, quantity, phone
  - Creates sending record
  - Logs action

- `get_all()` - Returns all dispatch records

**Access**: STAFF & ADMIN

**Database Table**: `sending`
- Columns: id, product_id, quantity, customer_contact, description, sent_by, created_at

---

### 4. **ReturnsService** (`services/returns_services.py`)
**Purpose**: Track product returns

**Key Methods**:
- `create_return(user_id, product_id, imei, colour, quantity, reason)`
  - Validates fields
  - Creates return record
  - Logs action

- `get_all()` - Returns all return records

**Access**: STAFF & ADMIN

**Database Table**: `returns`
- Columns: id, product_id, imei, colour, quantity, reason, recorded_by, created_at

---

### 5. **ProductService** (`services/product_service.py`)
**Purpose**: Manage product catalog

**Key Methods**:
- `create_product(user_id, name, brand, description)`
  - Validates no duplicates
  - Creates product record
  - Logs action

- `get_all()` - Returns all products

**Access**: ADMIN ONLY (not yet implemented in UI)

**Database Table**: `products`
- Columns: id, name, brand, description, created_at

---

### 6. **LogService** (`services/log_service.py`)
**Purpose**: Audit trail logging

**Key Methods**:
- `log(user_id, action, table_name, record_id)`
  - Records CRUD operations
  - Tracks user actions for compliance

**Access**: ADMIN ONLY (viewing)

**Database Table**: `logs`
- Columns: id, user_id, action, table_name, record_id, created_at

---

### 7. **AuthService** (`services/auth_service.py`)
**Purpose**: Authentication and authorization

**Key Methods**:
- `login(name, phone, password=None)`
  - Returns {"status": "SET_PASSWORD", "user": {...}} for first-time users
  - Returns {"status": "SUCCESS", "user": {...}} for existing users
  - Raises "Invalid credentials" for wrong password
  - Raises "User not found" if no matching user

- `set_password(user_id, password)` - Sets initial password

- `verify_password(user, password)` - Validates password

**Database Table**: `users`
- Columns: id, name, phone, password, role, created_at, updated_at

---

## ✅ Functionality Checklist

### Core Features
- [x] User Authentication (login with name/phone/password)
- [x] Role-based access (Admin vs Staff)
- [x] Stock Management (add/view inventory)
- [x] Sales Recording (plaza module)
- [x] Dispatch Management (sending module)
- [x] Returns Tracking (returns module)
- [x] Audit Logging (automatic action tracking)
- [x] Dashboard KPIs (stock, sales, dispatch, returns)
- [x] Low Stock Alerts (threshold-based warnings)

### Admin-Only Features
- [ ] Logs Viewer (implemented but not connected)
- [ ] User Management (stub only)
- [ ] Product Management (stub only)

### Data Validation
- [x] IMEI Validation (15 characters, unique)
- [x] Phone Number Validation
- [x] Quantity Validation (positive integers)
- [x] Product Existence Check
- [x] Duplicate Prevention

---

## 🧪 Test Credentials

**Admin User**:
- Name: Admin User
- Phone: 08000000000
- Password: admin123
- Role: admin

**Staff User**:
- Name: Staff User
- Phone: 08111111111
- Password: staff123
- Role: staff

---

## 🔧 Recent Fixes Applied

1. ✅ Fixed `auth_service.py` - Made password optional for first-time login
2. ✅ Fixed `dashboard.py` - Removed duplicate method definitions
3. ✅ Fixed `stock_service.py` - Removed non-existent batch_no column from INSERT
4. ✅ Enhanced `dashboard.py` - Added role display in sidebar header
5. ✅ Enhanced `dashboard.py` - Improved sidebar UI with emojis and role-based sections

---

## 📊 Database Schema Status

All required tables exist with correct schema:
- ✅ users (id, name, phone, password, role, created_at, updated_at)
- ✅ products (id, name, brand, description, created_at)
- ✅ stock (id, product_id, imei, colour, quantity, added_by, created_at)
- ✅ plaza (id, customer_name, customer_phone, product_id, imei, quantity, recorded_by, created_at)
- ✅ sending (id, product_id, quantity, customer_contact, description, sent_by, created_at)
- ✅ returns (id, product_id, imei, colour, quantity, reason, recorded_by, created_at)
- ✅ logs (id, user_id, action, table_name, record_id, created_at)

**Note**: users table is missing is_active, created_at, updated_at columns in some environments.
Run: `ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE, ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;`

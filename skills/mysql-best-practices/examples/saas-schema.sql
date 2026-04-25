-- Complete Multi-Tenant SaaS Schema Example
-- Production-grade schema following all best practices

CREATE DATABASE IF NOT EXISTS saas_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE saas_platform;

-- =============================================================================
-- Core Tables
-- =============================================================================

-- Tenants (Organizations/Franchises)
CREATE TABLE tenants (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Tenant ID',
  name VARCHAR(255) NOT NULL COMMENT 'Organization name',
  country_code CHAR(2) NOT NULL COMMENT 'ISO country code',
  timezone VARCHAR(40) NOT NULL DEFAULT 'UTC',
  status ENUM('active', 'suspended', 'deleted') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_name_country (name, country_code),
  KEY idx_country_code (country_code),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Organizations/Franchises';

-- Users
CREATE TABLE users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  user_type ENUM('super_admin', 'admin', 'staff', 'customer') NOT NULL DEFAULT 'staff',
  status ENUM('active', 'inactive', 'locked') NOT NULL DEFAULT 'active',
  last_login_at DATETIME,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
  UNIQUE KEY uk_username_tenant (tenant_id, username),
  UNIQUE KEY uk_email_tenant (tenant_id, email),
  KEY idx_tenant_status (tenant_id, status),
  KEY idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='System users';

-- Customers
CREATE TABLE customers (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(20),
  country_code CHAR(2) NOT NULL,
  credit_limit DECIMAL(13, 2) NOT NULL DEFAULT 0.00,
  total_orders INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Denormalized for performance',
  total_spent DECIMAL(13, 2) NOT NULL DEFAULT 0.00 COMMENT 'Denormalized',
  last_order_date DATETIME COMMENT 'Denormalized',
  status ENUM('active', 'inactive', 'blocked') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
  UNIQUE KEY uk_code_tenant (tenant_id, code),
  UNIQUE KEY uk_email_tenant (tenant_id, email),
  KEY idx_tenant_status (tenant_id, status),
  KEY idx_total_spent (tenant_id, total_spent DESC),
  KEY idx_last_order (tenant_id, last_order_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Customer records';

-- Products
CREATE TABLE products (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  unit_price DECIMAL(13, 2) NOT NULL,
  cost_price DECIMAL(13, 2) NOT NULL DEFAULT 0.00,
  stock_quantity INT NOT NULL DEFAULT 0,
  reorder_level INT NOT NULL DEFAULT 0,
  status ENUM('active', 'discontinued') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
  UNIQUE KEY uk_code_tenant (tenant_id, code),
  KEY idx_tenant_status (tenant_id, status),
  KEY idx_stock (tenant_id, stock_quantity),
  FULLTEXT INDEX ft_search (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Product catalog';

-- Orders
CREATE TABLE orders (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  customer_id INT UNSIGNED NOT NULL,
  order_number VARCHAR(50) NOT NULL,
  order_date DATE NOT NULL,
  total_amount DECIMAL(13, 2) NOT NULL DEFAULT 0.00,
  tax_amount DECIMAL(13, 2) NOT NULL DEFAULT 0.00,
  discount_amount DECIMAL(13, 2) NOT NULL DEFAULT 0.00,
  status ENUM('draft', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'draft',
  notes TEXT,
  created_by INT UNSIGNED,
  updated_by INT UNSIGNED,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
  FOREIGN KEY fk_customer (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
  FOREIGN KEY fk_created_by (created_by) REFERENCES users(id) ON DELETE SET NULL,
  UNIQUE KEY uk_order_number_tenant (tenant_id, order_number),
  KEY idx_tenant_customer (tenant_id, customer_id),
  KEY idx_tenant_date (tenant_id, order_date DESC),
  KEY idx_tenant_status (tenant_id, status),
  KEY idx_created_at (tenant_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Sales orders';

-- Order Items
CREATE TABLE order_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT UNSIGNED NOT NULL,
  product_id INT UNSIGNED NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(13, 2) NOT NULL,
  discount_percent DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
  line_total DECIMAL(13, 2) NOT NULL,

  FOREIGN KEY fk_order (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY fk_product (product_id) REFERENCES products(id) ON DELETE RESTRICT,
  UNIQUE KEY uk_order_product (order_id, product_id),
  KEY idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Order line items';

-- Payments
CREATE TABLE payments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  order_id BIGINT UNSIGNED NOT NULL,
  payment_number VARCHAR(50) NOT NULL,
  amount DECIMAL(13, 2) NOT NULL,
  payment_method ENUM('cash', 'mobile_money', 'bank_transfer', 'card') NOT NULL,
  payment_reference VARCHAR(100),
  payment_date DATE NOT NULL,
  status ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
  FOREIGN KEY fk_order (order_id) REFERENCES orders(id) ON DELETE RESTRICT,
  UNIQUE KEY uk_payment_number_tenant (tenant_id, payment_number),
  KEY idx_tenant_date (tenant_id, payment_date DESC),
  KEY idx_order (order_id),
  KEY idx_status (tenant_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Payment transactions';

-- =============================================================================
-- Audit and Logging
-- =============================================================================

-- Audit Log
CREATE TABLE audit_log (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(64) NOT NULL,
  record_id BIGINT UNSIGNED NOT NULL,
  operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  old_values JSON,
  new_values JSON,
  changed_by INT UNSIGNED,
  changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_table_record (table_name, record_id),
  KEY idx_changed_at (changed_at DESC),
  KEY idx_changed_by (changed_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Audit trail for all changes';

-- Activity Log
CREATE TABLE activity_log (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT UNSIGNED NOT NULL,
  user_id INT UNSIGNED NOT NULL,
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(50),
  entity_id BIGINT UNSIGNED,
  ip_address VARCHAR(45),
  user_agent VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY fk_user (user_id) REFERENCES users(id) ON DELETE CASCADE,
  KEY idx_tenant_user (tenant_id, user_id),
  KEY idx_created_at (created_at DESC),
  KEY idx_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User activity log';

-- =============================================================================
-- Sample Data
-- =============================================================================

-- Insert sample tenant
INSERT INTO tenants (name, country_code, timezone, status)
VALUES ('Acme Corporation', 'UG', 'Africa/Kampala', 'active');

-- Insert sample user
INSERT INTO users (tenant_id, username, email, password_hash, user_type, status)
VALUES (1, 'admin', 'admin@acme.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 'active');

-- Insert sample customer
INSERT INTO customers (tenant_id, code, name, email, phone, country_code, credit_limit, status)
VALUES (1, 'CUST001', 'John Doe', 'john@example.com', '+256700000000', 'UG', 1000000.00, 'active');

-- Insert sample product
INSERT INTO products (tenant_id, code, name, description, unit_price, cost_price, stock_quantity, status)
VALUES (1, 'PROD001', 'Sample Product', 'This is a sample product', 50000.00, 30000.00, 100, 'active');

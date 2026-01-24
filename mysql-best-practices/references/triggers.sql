-- Triggers for Data Integrity and Audit Trails
-- Complete examples for SaaS applications

-- =============================================================================
-- Audit Log Table
-- =============================================================================

CREATE TABLE audit_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(64) NOT NULL,
  record_id BIGINT NOT NULL,
  operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  old_values JSON,
  new_values JSON,
  changed_by INT UNSIGNED,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  KEY idx_table_operation (table_name, operation),
  KEY idx_record (table_name, record_id),
  KEY idx_changed_at (changed_at DESC),
  KEY idx_changed_by (changed_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- Audit Trail Triggers
-- =============================================================================

DELIMITER $

-- Track customer updates
CREATE TRIGGER tr_customers_audit_update
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values, changed_by)
  VALUES (
    'customers',
    NEW.id,
    'UPDATE',
    JSON_OBJECT(
      'email', OLD.email,
      'phone', OLD.phone,
      'status', OLD.status,
      'credit_limit', OLD.credit_limit
    ),
    JSON_OBJECT(
      'email', NEW.email,
      'phone', NEW.phone,
      'status', NEW.status,
      'credit_limit', NEW.credit_limit
    ),
    COALESCE(@current_user_id, NULL)
  );
END$

-- Track customer deletions
CREATE TRIGGER tr_customers_audit_delete
AFTER DELETE ON customers
FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, record_id, operation, old_values, changed_by)
  VALUES (
    'customers',
    OLD.id,
    'DELETE',
    JSON_OBJECT(
      'email', OLD.email,
      'phone', OLD.phone,
      'status', OLD.status
    ),
    COALESCE(@current_user_id, NULL)
  );
END$

DELIMITER ;

-- Usage: Set user context before DML
-- SET @current_user_id = 123;
-- UPDATE customers SET email = 'new@example.com' WHERE id = 456;

-- =============================================================================
-- Data Consistency Triggers
-- =============================================================================

DELIMITER $

-- Update order total when items are added
CREATE TRIGGER tr_order_items_insert_after
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
  UPDATE orders
  SET total_amount = (
    SELECT SUM(quantity * unit_price)
    FROM order_items
    WHERE order_id = NEW.order_id
  ),
  updated_at = NOW()
  WHERE id = NEW.order_id;

  -- Check inventory
  IF (SELECT stock_quantity FROM products WHERE id = NEW.product_id) < 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Insufficient inventory';
  END IF;
END$

-- Update order total when items are modified
CREATE TRIGGER tr_order_items_update_after
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
  UPDATE orders
  SET total_amount = (
    SELECT SUM(quantity * unit_price)
    FROM order_items
    WHERE order_id = NEW.order_id
  ),
  updated_at = NOW()
  WHERE id = NEW.order_id;
END$

-- Update order total when items are deleted
CREATE TRIGGER tr_order_items_delete_after
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
  UPDATE orders
  SET total_amount = (
    SELECT COALESCE(SUM(quantity * unit_price), 0)
    FROM order_items
    WHERE order_id = OLD.order_id
  ),
  updated_at = NOW()
  WHERE id = OLD.order_id;
END$

DELIMITER ;

-- =============================================================================
-- Denormalized Counter Updates
-- =============================================================================

DELIMITER $

-- Update customer's order count and total spent
CREATE TRIGGER tr_orders_insert_after
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
  UPDATE customers
  SET total_orders = total_orders + 1,
      total_spent = total_spent + NEW.total_amount,
      last_order_date = NEW.order_date
  WHERE id = NEW.customer_id;
END$

CREATE TRIGGER tr_orders_update_after
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
  IF NEW.total_amount != OLD.total_amount THEN
    UPDATE customers
    SET total_spent = total_spent - OLD.total_amount + NEW.total_amount
    WHERE id = NEW.customer_id;
  END IF;
END$

CREATE TRIGGER tr_orders_delete_after
AFTER DELETE ON orders
FOR EACH ROW
BEGIN
  UPDATE customers
  SET total_orders = total_orders - 1,
      total_spent = total_spent - OLD.total_amount,
      last_order_date = (
        SELECT MAX(order_date) FROM orders WHERE customer_id = OLD.customer_id
      )
  WHERE id = OLD.customer_id;
END$

DELIMITER ;

-- =============================================================================
-- Prevention Triggers
-- =============================================================================

DELIMITER $

-- Prevent deletion of active subscriptions
CREATE TRIGGER tr_prevent_delete_active_subscriptions
BEFORE DELETE ON subscriptions
FOR EACH ROW
BEGIN
  IF OLD.status = 'active' THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Cannot delete active subscriptions. Cancel first.';
  END IF;
END$

-- Prevent updating paid invoices
CREATE TRIGGER tr_prevent_update_paid_invoices
BEFORE UPDATE ON invoices
FOR EACH ROW
BEGIN
  IF OLD.status = 'paid' AND NEW.status != OLD.status THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Cannot modify status of paid invoices';
  END IF;
END$

-- Enforce tenant isolation
CREATE TRIGGER tr_prevent_cross_tenant_insert
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  DECLARE v_customer_tenant_id INT;

  SELECT tenant_id INTO v_customer_tenant_id
  FROM customers
  WHERE id = NEW.customer_id;

  IF v_customer_tenant_id != NEW.tenant_id THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Cross-tenant data access violation';
  END IF;
END$

DELIMITER ;

-- =============================================================================
-- Validation Triggers
-- =============================================================================

DELIMITER $

-- Validate email format
CREATE TRIGGER tr_validate_customer_email
BEFORE INSERT ON customers
FOR EACH ROW
BEGIN
  IF NEW.email IS NOT NULL AND NEW.email NOT LIKE '%_@__%.__%' THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Invalid email format';
  END IF;
END$

-- Validate date ranges
CREATE TRIGGER tr_validate_subscription_dates
BEFORE INSERT ON subscriptions
FOR EACH ROW
BEGIN
  IF NEW.end_date IS NOT NULL AND NEW.end_date < NEW.start_date THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'End date must be after start date';
  END IF;
END$

-- Validate amounts
CREATE TRIGGER tr_validate_transaction_amount
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
  IF NEW.amount <= 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Transaction amount must be positive';
  END IF;
END$

DELIMITER ;

-- =============================================================================
-- Automatic Timestamping
-- =============================================================================

DELIMITER $

-- Set created_by and updated_by from session variable
CREATE TRIGGER tr_set_created_by
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  SET NEW.created_by = COALESCE(@current_user_id, NULL);
  SET NEW.updated_by = COALESCE(@current_user_id, NULL);
END$

CREATE TRIGGER tr_set_updated_by
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
  SET NEW.updated_by = COALESCE(@current_user_id, NULL);
END$

DELIMITER ;

-- Usage:
-- SET @current_user_id = 123;
-- INSERT INTO orders (...) VALUES (...);

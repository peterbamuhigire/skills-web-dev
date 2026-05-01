-- Stored Procedures and Functions for SaaS Applications
-- Complete examples with transaction safety, error handling, and best practices

-- =============================================================================
-- Transactional Payment Processing
-- =============================================================================

DELIMITER $

CREATE PROCEDURE sp_process_order_payment(
  IN p_order_id BIGINT,
  IN p_amount DECIMAL(13, 2),
  IN p_payment_method VARCHAR(50),
  OUT p_success BOOLEAN,
  OUT p_error_message VARCHAR(255)
)
READS SQL DATA
MODIFIES SQL DATA
SQL SECURITY INVOKER
COMMENT 'Process order payment with transaction safety'
BEGIN
  DECLARE v_customer_id INT;
  DECLARE v_current_balance DECIMAL(13, 2);

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    SET p_success = FALSE;
    SET p_error_message = 'Transaction failed and rolled back';
  END;

  START TRANSACTION;

  -- Lock the order to prevent concurrent modifications
  SELECT customer_id INTO v_customer_id
  FROM orders
  WHERE id = p_order_id
  FOR UPDATE;

  -- Validate customer exists and has sufficient balance
  SELECT account_balance INTO v_current_balance
  FROM customer_accounts
  WHERE customer_id = v_customer_id
  FOR UPDATE;

  IF v_current_balance < p_amount THEN
    ROLLBACK;
    SET p_success = FALSE;
    SET p_error_message = 'Insufficient balance';
  ELSE
    -- Deduct amount from account
    UPDATE customer_accounts
    SET account_balance = account_balance - p_amount
    WHERE customer_id = v_customer_id;

    -- Record payment transaction
    INSERT INTO payment_transactions
    (order_id, customer_id, amount, payment_method, status)
    VALUES (p_order_id, v_customer_id, p_amount, p_payment_method, 'completed');

    -- Update order status
    UPDATE orders
    SET status = 'paid', paid_date = NOW()
    WHERE id = p_order_id;

    COMMIT;
    SET p_success = TRUE;
    SET p_error_message = NULL;
  END IF;
END$

DELIMITER ;

-- Usage:
-- CALL sp_process_order_payment(12345, 150.00, 'mobile_money', @success, @error);
-- SELECT @success, @error;

-- =============================================================================
-- Bulk Import with Batching
-- =============================================================================

DELIMITER $

CREATE PROCEDURE sp_bulk_import_transactions(
  IN p_tenant_id INT,
  IN p_batch_size INT
)
MODIFIES SQL DATA
SQL SECURITY INVOKER
COMMENT 'Efficiently imports transactions from staging table'
BEGIN
  DECLARE v_rows_processed INT DEFAULT 0;
  DECLARE v_total_rows INT;

  SELECT COUNT(*) INTO v_total_rows
  FROM staging_transactions
  WHERE tenant_id = p_tenant_id AND processed = FALSE;

  WHILE v_rows_processed < v_total_rows DO
    START TRANSACTION;

    -- Process batch of records
    INSERT INTO transactions (tenant_id, user_id, amount, currency, status)
    SELECT tenant_id, user_id, amount, currency, 'pending'
    FROM staging_transactions
    WHERE tenant_id = p_tenant_id
      AND processed = FALSE
    LIMIT p_batch_size;

    -- Mark as processed
    UPDATE staging_transactions
    SET processed = TRUE, processed_date = NOW()
    WHERE tenant_id = p_tenant_id
      AND processed = FALSE
    LIMIT p_batch_size;

    COMMIT;

    SET v_rows_processed = v_rows_processed + p_batch_size;

    -- Allow other transactions to proceed
    DO SLEEP(0.1);
  END WHILE;
END$

DELIMITER ;

-- Usage:
-- CALL sp_bulk_import_transactions(1, 500);

-- =============================================================================
-- Funds Transfer with Deadlock Prevention
-- =============================================================================

DELIMITER $

CREATE PROCEDURE sp_transfer_funds(
  IN p_from_account_id INT,
  IN p_to_account_id INT,
  IN p_amount DECIMAL(13, 2)
)
MODIFIES SQL DATA
SQL SECURITY INVOKER
COMMENT 'Transfer funds between accounts with deadlock prevention'
BEGIN
  DECLARE v_from_balance DECIMAL(13, 2);
  DECLARE v_to_balance DECIMAL(13, 2);

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;

  -- Lock accounts in consistent order (prevents deadlocks)
  SELECT balance INTO v_from_balance
  FROM accounts
  WHERE id = LEAST(p_from_account_id, p_to_account_id)
  FOR UPDATE;

  SELECT balance INTO v_to_balance
  FROM accounts
  WHERE id = GREATEST(p_from_account_id, p_to_account_id)
  FOR UPDATE;

  -- Get actual balances
  SELECT balance INTO v_from_balance FROM accounts WHERE id = p_from_account_id;
  SELECT balance INTO v_to_balance FROM accounts WHERE id = p_to_account_id;

  -- Verify sufficient funds
  IF v_from_balance < p_amount THEN
    ROLLBACK;
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient funds';
  ELSE
    UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_account_id;
    UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_account_id;

    -- Log transaction
    INSERT INTO transfer_log (from_account, to_account, amount, transfer_date)
    VALUES (p_from_account_id, p_to_account_id, p_amount, NOW());

    COMMIT;
  END IF;
END$

DELIMITER ;

-- Usage:
-- CALL sp_transfer_funds(100, 200, 50.00);

-- =============================================================================
-- Calculation Function
-- =============================================================================

DELIMITER $

CREATE FUNCTION fn_calculate_order_total(
  p_order_id BIGINT
) RETURNS DECIMAL(13, 2)
READS SQL DATA
DETERMINISTIC
SQL SECURITY INVOKER
COMMENT 'Calculate total including tax and discounts'
BEGIN
  DECLARE v_subtotal DECIMAL(13, 2);
  DECLARE v_tax_rate DECIMAL(5, 4);
  DECLARE v_discount DECIMAL(13, 2);

  SELECT SUM(quantity * unit_price)
  INTO v_subtotal
  FROM order_items
  WHERE order_id = p_order_id;

  SELECT tax_percentage / 100
  INTO v_tax_rate
  FROM orders o
  JOIN jurisdictions j ON o.jurisdiction_id = j.id
  WHERE o.id = p_order_id;

  SELECT COALESCE(discount_amount, 0)
  INTO v_discount
  FROM order_discounts
  WHERE order_id = p_order_id;

  RETURN ROUND((v_subtotal - v_discount) * (1 + v_tax_rate), 2);
END$

DELIMITER ;

-- Usage:
-- SELECT id, fn_calculate_order_total(id) as total FROM orders;

-- =============================================================================
-- Permission Check Function
-- =============================================================================

DELIMITER $

CREATE FUNCTION fn_has_permission(
  p_user_id INT,
  p_tenant_id INT,
  p_permission_code VARCHAR(50)
) RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
SQL SECURITY INVOKER
COMMENT 'Check if user has specific permission in tenant'
BEGIN
  DECLARE v_has_perm BOOLEAN DEFAULT FALSE;

  -- Check if super admin
  SELECT user_type = 'super_admin' INTO v_has_perm
  FROM users WHERE id = p_user_id;

  IF v_has_perm THEN
    RETURN TRUE;
  END IF;

  -- Check direct permissions or role-based permissions
  SELECT COUNT(*) > 0 INTO v_has_perm
  FROM user_roles ur
  JOIN role_permissions rp ON ur.role_id = rp.role_id
  JOIN permissions p ON rp.permission_id = p.id
  WHERE ur.user_id = p_user_id
    AND ur.tenant_id = p_tenant_id
    AND p.code = p_permission_code;

  RETURN v_has_perm;
END$

DELIMITER ;

-- Usage:
-- SELECT fn_has_permission(123, 1, 'MANAGE_INVOICES');

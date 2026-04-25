-- Complete Database Schema for Dual Auth + RBAC System
-- Multi-tenant with franchise-scoped permissions
-- Compatible with MySQL 8.0+, MariaDB 10.5+, PostgreSQL 12+

-- ============================================
-- CORE USER TABLE
-- ============================================

CREATE TABLE tbl_users (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NULL COMMENT 'NULL for super_admin',
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'Argon2ID with salt+pepper',
    user_type ENUM('super_admin', 'owner', 'distributor', 'staff') NOT NULL DEFAULT 'staff',
    status ENUM('active', 'inactive', 'locked', 'pending', 'invited', 'suspended') NOT NULL DEFAULT 'pending',
    failed_login_attempts SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    last_login DATETIME NULL,
    force_password_change TINYINT(1) NOT NULL DEFAULT 1,
    password_reset_token VARCHAR(100) NULL,
    password_reset_expires DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email_franchise (email, franchise_id),
    INDEX idx_franchise_status (franchise_id, status),
    INDEX idx_user_type (user_type),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- GLOBAL ROLES (Reusable Across Tenants)
-- ============================================

CREATE TABLE tbl_global_roles (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'System roles cannot be deleted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed default roles
INSERT INTO tbl_global_roles (code, name, description, is_system) VALUES
('SUPER_ADMIN', 'Super Administrator', 'Full system access', 1),
('FRANCHISE_OWNER', 'Franchise Owner', 'Full franchise management', 1),
('MANAGER', 'Manager', 'Day-to-day operations', 1),
('CASHIER', 'Cashier', 'Sales and payments', 1),
('INVENTORY_CLERK', 'Inventory Clerk', 'Stock management', 1),
('VIEWER', 'Viewer', 'Read-only access', 1);

-- ============================================
-- PERMISSION DEFINITIONS
-- ============================================

CREATE TABLE tbl_permissions (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE COMMENT 'e.g., USER_CREATE, INVOICE_VIEW',
    name VARCHAR(100) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL COMMENT 'Feature module grouping',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_module (module),
    CONSTRAINT chk_code_format CHECK (code REGEXP '^[A-Z][A-Z0-9_]{2,49}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed default permissions
INSERT INTO tbl_permissions (code, name, description, module) VALUES
-- User Management
('USER_VIEW', 'View Users', 'View user list and details', 'user_management'),
('USER_CREATE', 'Create Users', 'Add new users', 'user_management'),
('USER_EDIT', 'Edit Users', 'Modify user details', 'user_management'),
('USER_DELETE', 'Delete Users', 'Remove users', 'user_management'),
('USER_ASSIGN_ROLES', 'Assign Roles', 'Manage user roles', 'user_management'),

-- Sales
('SALE_VIEW', 'View Sales', 'View sale transactions', 'sales'),
('SALE_CREATE', 'Create Sales', 'Process sales', 'sales'),
('SALE_VOID', 'Void Sales', 'Cancel sales', 'sales'),
('SALE_REFUND', 'Refund Sales', 'Process refunds', 'sales'),

-- Inventory
('INVENTORY_VIEW', 'View Inventory', 'View stock levels', 'inventory'),
('INVENTORY_ADJUST', 'Adjust Inventory', 'Modify stock levels', 'inventory'),
('INVENTORY_TRANSFER', 'Transfer Inventory', 'Move stock between locations', 'inventory'),

-- Reports
('REPORT_SALES', 'Sales Reports', 'View sales reports', 'reports'),
('REPORT_INVENTORY', 'Inventory Reports', 'View inventory reports', 'reports'),
('REPORT_FINANCIAL', 'Financial Reports', 'View financial reports', 'reports'),

-- Settings
('SETTINGS_VIEW', 'View Settings', 'View system settings', 'settings'),
('SETTINGS_EDIT', 'Edit Settings', 'Modify system settings', 'settings');

-- ============================================
-- ROLE-PERMISSION MAPPING
-- ============================================

CREATE TABLE tbl_global_role_permissions (
    global_role_id BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (global_role_id, permission_id),
    FOREIGN KEY (global_role_id) REFERENCES tbl_global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES tbl_permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Seed role permissions (example for MANAGER role)
INSERT INTO tbl_global_role_permissions (global_role_id, permission_id)
SELECT r.id, p.id
FROM tbl_global_roles r
CROSS JOIN tbl_permissions p
WHERE r.code = 'MANAGER'
  AND p.code IN (
    'USER_VIEW', 'SALE_VIEW', 'SALE_CREATE', 'SALE_VOID',
    'INVENTORY_VIEW', 'REPORT_SALES', 'REPORT_INVENTORY', 'SETTINGS_VIEW'
  );

-- ============================================
-- USER-ROLE ASSIGNMENTS (Franchise-Scoped)
-- ============================================

CREATE TABLE tbl_user_roles (
    user_id BIGINT UNSIGNED NOT NULL,
    global_role_id BIGINT UNSIGNED NOT NULL,
    franchise_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, global_role_id, franchise_id),
    FOREIGN KEY (user_id) REFERENCES tbl_users(id) ON DELETE CASCADE,
    FOREIGN KEY (global_role_id) REFERENCES tbl_global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- DIRECT USER PERMISSION OVERRIDES
-- ============================================

CREATE TABLE tbl_user_permissions (
    user_id BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    franchise_id BIGINT UNSIGNED NOT NULL,
    allowed TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=grant, 0=deny (overrides role)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, permission_id, franchise_id),
    FOREIGN KEY (user_id) REFERENCES tbl_users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES tbl_permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- FRANCHISE-LEVEL ROLE PERMISSION OVERRIDES
-- ============================================

CREATE TABLE tbl_franchise_role_overrides (
    franchise_id BIGINT UNSIGNED NOT NULL,
    global_role_id BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    is_enabled TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (franchise_id, global_role_id, permission_id),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (global_role_id) REFERENCES tbl_global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES tbl_permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- JWT REFRESH TOKEN STORAGE (Revocation)
-- ============================================

CREATE TABLE tbl_api_refresh_tokens (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    franchise_id BIGINT UNSIGNED NULL,
    jti VARCHAR(64) NOT NULL UNIQUE COMMENT 'JWT ID for revocation lookup',
    device_id VARCHAR(128) NULL COMMENT 'Optional device binding',
    is_revoked TINYINT(1) NOT NULL DEFAULT 0,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_device (user_id, device_id),
    INDEX idx_jti (jti),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (user_id) REFERENCES tbl_users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- LOGIN ATTEMPT TRACKING
-- ============================================

CREATE TABLE tbl_login_attempts (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    attempt_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success TINYINT(1) NOT NULL DEFAULT 0,
    failure_reason VARCHAR(50) NULL COMMENT 'e.g., WRONG_PASSWORD, ACCOUNT_LOCKED',

    INDEX idx_username_time (username, attempt_time),
    INDEX idx_ip_time (ip_address, attempt_time),
    INDEX idx_attempt_time (attempt_time)
) ENGINE=InnoDB;

-- ============================================
-- STORED PROCEDURE: Permission Resolution
-- ============================================

DELIMITER $$

CREATE PROCEDURE sp_get_user_permissions(
    IN p_user_id BIGINT,
    IN p_franchise_id BIGINT
)
BEGIN
    -- Collect all permissions for a user considering:
    -- 1. Role-based permissions (tbl_global_role_permissions)
    -- 2. Franchise-level overrides (tbl_franchise_role_overrides)
    -- 3. Direct user grants/denials (tbl_user_permissions)

    SELECT
        p_user_id AS user_id,
        p_franchise_id AS franchise_id,
        GROUP_CONCAT(DISTINCT gr.name ORDER BY gr.name SEPARATOR ', ') AS roles,
        GROUP_CONCAT(DISTINCT gr.code ORDER BY gr.code SEPARATOR ',') AS role_codes,
        (
            SELECT GROUP_CONCAT(DISTINCT final_perms.code ORDER BY final_perms.code SEPARATOR ',')
            FROM (
                -- Role-based permissions
                SELECT p.code
                FROM tbl_user_roles ur
                JOIN tbl_global_role_permissions grp ON ur.global_role_id = grp.global_role_id
                JOIN tbl_permissions p ON grp.permission_id = p.id
                LEFT JOIN tbl_franchise_role_overrides fro
                    ON fro.franchise_id = p_franchise_id
                    AND fro.global_role_id = ur.global_role_id
                    AND fro.permission_id = p.id
                WHERE ur.user_id = p_user_id
                    AND ur.franchise_id = p_franchise_id
                    AND (fro.is_enabled IS NULL OR fro.is_enabled = 1)

                UNION

                -- Direct user permission grants
                SELECT p.code
                FROM tbl_user_permissions up
                JOIN tbl_permissions p ON up.permission_id = p.id
                WHERE up.user_id = p_user_id
                    AND up.franchise_id = p_franchise_id
                    AND up.allowed = 1
            ) AS granted_perms
            WHERE granted_perms.code NOT IN (
                -- Exclude explicitly denied permissions
                SELECT p.code
                FROM tbl_user_permissions up
                JOIN tbl_permissions p ON up.permission_id = p.id
                WHERE up.user_id = p_user_id
                    AND up.franchise_id = p_franchise_id
                    AND up.allowed = 0
            )
        ) AS permissions
    FROM tbl_user_roles ur
    JOIN tbl_global_roles gr ON ur.global_role_id = gr.id
    WHERE ur.user_id = p_user_id AND ur.franchise_id = p_franchise_id;

END$$

DELIMITER ;

-- ============================================
-- CLEANUP JOB: Remove Expired Tokens
-- ============================================

-- Run this as a scheduled job (cron/scheduled task)
-- DELETE FROM tbl_api_refresh_tokens WHERE expires_at < NOW() OR is_revoked = 1;
-- DELETE FROM tbl_login_attempts WHERE attempt_time < DATE_SUB(NOW(), INTERVAL 90 DAY);

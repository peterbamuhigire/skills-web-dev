<?php
/**
 * Example Module Configuration
 *
 * This file shows how to configure a new module in the Maduuka SAAS platform.
 * Place this file in: modules/{module-name}/module.config.php
 */

return [
    // Unique identifier for the module (uppercase, underscores)
    'module_code' => 'ADV_INV',

    // Display name shown to users
    'name' => 'Advanced Inventory',

    // Brief description of what this module does
    'description' => 'Multi-location inventory management with UOM conversions, stock transfers, and advanced reporting',

    // Current version (semantic versioning)
    'version' => '1.0.0',

    // Bootstrap icon class for UI display
    'icon' => 'bi-boxes',

    // Author information
    'author' => 'Maduuka Development Team',
    'author_email' => 'dev@maduuka.com',

    // Minimum system requirements
    'min_php_version' => '8.0',
    'min_mysql_version' => '8.0',

    // Module category for organization
    'category' => 'inventory',  // inventory, sales, hr, finance, etc.

    // Module dependencies (other modules that must be enabled)
    'requires' => [
        // No dependencies = module works standalone
    ],
    // Example with dependencies:
    // 'requires' => ['CORE', 'RETAIL'],  // Requires Core and Retail modules

    // Optional modules that enhance this module if available
    'enhances_with' => [
        'RETAIL',      // If Retail enabled, POS can use advanced inventory
        'RESTAURANT',  // If Restaurant enabled, orders can use advanced inventory
    ],

    // Features provided by this module
    'features' => [
        'stock_items' => [
            'name' => 'Stock Item Management',
            'description' => 'Create and manage stock items with photos, categories, and pricing',
        ],
        'uom_conversions' => [
            'name' => 'Unit of Measure Conversions',
            'description' => 'Define multiple units for each stock item (e.g., boxes, pieces, grams)',
        ],
        'stock_transfers' => [
            'name' => 'Stock Transfers',
            'description' => 'Transfer stock between locations with approval workflow',
        ],
        'multi_location_inventory' => [
            'name' => 'Multi-Location Inventory',
            'description' => 'Track inventory levels across multiple branches',
        ],
        'stock_adjustments' => [
            'name' => 'Stock Adjustments',
            'description' => 'Adjust inventory levels with reason tracking',
        ],
        'inventory_reports' => [
            'name' => 'Inventory Reports',
            'description' => 'Stock movement reports, valuation, and analytics',
        ],
    ],

    // Permissions defined by this module
    'permissions' => [
        [
            'code' => 'VIEW_INVENTORY',
            'name' => 'View Inventory',
            'description' => 'View stock items and inventory levels',
            'category' => 'read',
        ],
        [
            'code' => 'MANAGE_STOCK',
            'name' => 'Manage Stock',
            'description' => 'Create, edit, and delete stock items',
            'category' => 'write',
        ],
        [
            'code' => 'APPROVE_TRANSFERS',
            'name' => 'Approve Stock Transfers',
            'description' => 'Approve or reject stock transfer requests',
            'category' => 'approve',
        ],
        [
            'code' => 'VIEW_REPORTS',
            'name' => 'View Inventory Reports',
            'description' => 'Access inventory reports and analytics',
            'category' => 'read',
        ],
    ],

    // Database tables owned by this module
    'tables' => [
        'tbl_stock_items',
        'tbl_stock_item_uoms',
        'tbl_stock_transfers',
        'tbl_stock_transfer_items',
        'tbl_stock_adjustments',
        'tbl_inventory_transactions',
        'tbl_inventory_locations',
    ],

    // Navigation menu structure
    'menu' => [
        [
            'label' => 'Inventory',
            'icon' => 'bi-boxes',
            'url' => null,  // null = dropdown
            'permission' => 'VIEW_INVENTORY',
            'items' => [
                [
                    'label' => 'Stock Items',
                    'url' => '/stock-items-catalog.php',
                    'icon' => 'bi-box',
                    'permission' => 'VIEW_INVENTORY',
                ],
                [
                    'label' => 'UOM Conversions',
                    'url' => '/advanced-inventory-uom.php',
                    'icon' => 'bi-rulers',
                    'permission' => 'VIEW_INVENTORY',
                ],
                [
                    'label' => 'Stock Transfers',
                    'url' => '/stock-transfers.php',
                    'icon' => 'bi-arrow-left-right',
                    'permission' => 'VIEW_INVENTORY',
                ],
                [
                    'label' => 'Stock Adjustments',
                    'url' => '/stock-adjustments.php',
                    'icon' => 'bi-sliders',
                    'permission' => 'MANAGE_STOCK',
                ],
                [
                    'label' => 'Reports',
                    'url' => '/inventory-reports.php',
                    'icon' => 'bi-graph-up',
                    'permission' => 'VIEW_REPORTS',
                ],
            ],
        ],
    ],

    // Pricing tiers for this module
    'pricing' => [
        'tiers' => [
            [
                'tier' => 'basic',
                'price_monthly' => 29.99,
                'price_yearly' => 299.90,  // ~17% discount
                'trial_days' => 14,
                'features_limit' => [
                    'stock_items' => 1000,
                    'locations' => 3,
                    'transfers_per_month' => 100,
                ],
            ],
            [
                'tier' => 'premium',
                'price_monthly' => 59.99,
                'price_yearly' => 599.90,
                'trial_days' => 14,
                'features_limit' => [
                    'stock_items' => -1,  // Unlimited
                    'locations' => -1,
                    'transfers_per_month' => -1,
                ],
            ],
        ],
    ],

    // API endpoints exposed by this module
    'api_endpoints' => [
        [
            'path' => '/api/advanced-inventory/stock-items.php',
            'description' => 'Stock item CRUD operations',
            'methods' => ['GET', 'POST', 'PUT', 'DELETE'],
        ],
        [
            'path' => '/api/advanced-inventory/uoms.php',
            'description' => 'UOM conversion management',
            'methods' => ['GET', 'POST', 'PUT', 'DELETE'],
        ],
        [
            'path' => '/api/advanced-inventory/transfers.php',
            'description' => 'Stock transfer operations',
            'methods' => ['GET', 'POST', 'PUT'],
        ],
    ],

    // Webhook events dispatched by this module
    'events' => [
        'stock_item.created' => 'Fired when a new stock item is created',
        'stock_item.updated' => 'Fired when a stock item is updated',
        'stock_item.deleted' => 'Fired when a stock item is deleted',
        'stock_transfer.requested' => 'Fired when a transfer is requested',
        'stock_transfer.approved' => 'Fired when a transfer is approved',
        'stock_transfer.completed' => 'Fired when a transfer is completed',
        'inventory.low_stock' => 'Fired when stock falls below reorder level',
    ],

    // Settings/configuration options for this module
    'settings' => [
        [
            'key' => 'auto_approve_transfers',
            'name' => 'Auto-approve Transfers',
            'description' => 'Automatically approve stock transfers without manual approval',
            'type' => 'boolean',
            'default' => false,
        ],
        [
            'key' => 'default_costing_method',
            'name' => 'Default Costing Method',
            'description' => 'Method used for inventory valuation',
            'type' => 'select',
            'options' => ['FIFO', 'LIFO', 'Average Cost'],
            'default' => 'FIFO',
        ],
        [
            'key' => 'low_stock_threshold',
            'name' => 'Low Stock Threshold %',
            'description' => 'Alert when stock falls below this percentage of reorder level',
            'type' => 'number',
            'default' => 20,
            'min' => 0,
            'max' => 100,
        ],
    ],

    // Installation/setup instructions
    'installation' => [
        'migrations_path' => __DIR__ . '/database/migrations',
        'seeds_path' => __DIR__ . '/database/seeds',
        'post_install_hook' => __DIR__ . '/hooks/post-install.php',
    ],

    // Documentation links
    'documentation' => [
        'user_guide' => 'https://docs.maduuka.com/modules/advanced-inventory',
        'api_reference' => 'https://docs.maduuka.com/api/advanced-inventory',
        'changelog' => 'https://docs.maduuka.com/modules/advanced-inventory/changelog',
    ],

    // Support information
    'support' => [
        'email' => 'support@maduuka.com',
        'documentation' => 'https://docs.maduuka.com/modules/advanced-inventory',
        'video_tutorials' => 'https://youtube.com/maduuka-inventory',
    ],
];

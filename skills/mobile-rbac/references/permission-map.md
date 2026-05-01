# Permission Map - Feature-to-Permission Reference

## Module Gating (Tab Visibility)

| Tab | Module Code | Default |
|-----|-------------|---------|
| Dashboard | _(none)_ | Always visible |
| POS | `POS` | Hidden if not subscribed |
| Inventory | `INVENTORY` | Hidden if not subscribed |
| Customers | `CUSTOMERS` | Hidden if not subscribed |
| Settings | _(none)_ | Always visible |

## Permission Gating (Screen & Action Level)

### Gating Types

| Type | Behavior | Use For |
|------|----------|---------|
| **Tab hide** | Bottom nav item removed | Module not subscribed |
| **Card hide** | Card/section not rendered | Navigation cards without access |
| **FAB hide** | Create button not shown | User can't create new items |
| **Button disable** | Greyed out + message text | User can see but can't perform action |
| **Nav guard** | Redirects to PermissionDeniedScreen | Deep link / URL protection |
| **Screen gate** | Shows empty/denied state | Full screen requires permission |

### Dashboard

| Element | Permission | Type |
|---------|-----------|------|
| View KPIs | `DASHBOARD_VIEW` | Always shown |
| Today's Sales section | `DASHBOARD_VIEW_SALES` | Card hide |
| Recent Transactions | `DASHBOARD_VIEW_TRANSACTIONS` | Card hide |

### POS

| Element | Permission | Type |
|---------|-----------|------|
| POS tab | Module: `POS` | Tab hide |
| View products | `POS_VIEW_PRODUCTS` | Screen gate |
| Add to cart | `POS_CREATE_SALE` | Button disable |
| "Charge" button | `POS_CREATE_SALE` | Button disable |
| "Credit Sale" | `POS_CREDIT_SALE` | Button hide |
| View receipts | `POS_VIEW_RECEIPTS` | Button hide |

### Inventory Home

| Element | Permission | Type |
|---------|-----------|------|
| Inventory tab | Module: `INVENTORY` | Tab hide |
| Stock levels list | `INVENTORY_VIEW` | Screen gate |
| PO card | `INVENTORY_PO_VIEW` | Card hide |
| Transfers card | `INVENTORY_TRANSFER_VIEW` | Card hide |
| Adjustments card | `INVENTORY_ADJUSTMENT_VIEW` | Card hide |
| Reports card | `REPORTS_VIEW` | Card hide |

### Purchase Orders

| Element | Permission | Type |
|---------|-----------|------|
| View PO list | `INVENTORY_PO_VIEW` | Nav guard |
| Create PO (FAB) | `INVENTORY_PO_CREATE` | FAB hide |
| Create PO screen | `INVENTORY_PO_CREATE` | Nav guard |
| View PO detail | `INVENTORY_PO_VIEW` | Nav guard |
| Add item (FAB) | `INVENTORY_PO_ADD_ITEM` | FAB hide |
| Approve button | `INVENTORY_PO_APPROVE` | Button disable |
| Receive button | `INVENTORY_PO_RECEIVE` | Button disable |

### Stock Transfers

| Element | Permission | Type |
|---------|-----------|------|
| View list | `INVENTORY_TRANSFER_VIEW` | Nav guard |
| Create (FAB) | `INVENTORY_TRANSFER_CREATE` | FAB hide |
| Create screen | `INVENTORY_TRANSFER_CREATE` | Nav guard |
| View detail | `INVENTORY_TRANSFER_VIEW` | Nav guard |
| Add item (FAB) | `INVENTORY_TRANSFER_ADD_ITEM` | FAB hide |
| Dispatch button | `INVENTORY_TRANSFER_DISPATCH` | Button disable |
| Receive button | `INVENTORY_TRANSFER_RECEIVE` | Button disable |

### Stock Adjustments

| Element | Permission | Type |
|---------|-----------|------|
| View list | `INVENTORY_ADJUSTMENT_VIEW` | Nav guard |
| Create (FAB) | `INVENTORY_ADJUSTMENT_CREATE` | FAB hide |
| Create screen | `INVENTORY_ADJUSTMENT_CREATE` | Nav guard |
| View detail | `INVENTORY_ADJUSTMENT_VIEW` | Nav guard |
| Add item (FAB) | `INVENTORY_ADJUSTMENT_ADD_ITEM` | FAB hide |
| Approve button | `INVENTORY_ADJUSTMENT_APPROVE` | Button disable |

### Reports

| Element | Permission | Type |
|---------|-----------|------|
| Reports section | `REPORTS_VIEW` | Card hide (from Inv Home) |
| Stock Levels | `REPORTS_STOCK_LEVELS` | Card hide + Nav guard |
| Stock Movements | `REPORTS_STOCK_MOVEMENTS` | Card hide + Nav guard |
| Inventory Valuation | `REPORTS_INVENTORY_VALUATION` | Card hide + Nav guard |
| Purchase Orders | `REPORTS_PURCHASE_ORDERS` | Card hide + Nav guard |
| Stock Transfers | `REPORTS_STOCK_TRANSFERS` | Card hide + Nav guard |
| Demand Forecasting | `REPORTS_DEMAND_FORECASTING` | Card hide + Nav guard |
| Profitability | `REPORTS_PROFITABILITY` | Card hide + Nav guard |
| Compliance Audit | `REPORTS_COMPLIANCE_AUDIT` | Card hide + Nav guard |

### Settings

| Element | Permission | Type |
|---------|-----------|------|
| Settings tab | _(none)_ | Always visible |
| About dialog | _(none)_ | Always accessible |
| Logout | _(none)_ | Always accessible |
| Manage settings | `SETTINGS_MANAGE` | Show/hide |

### Customers (Future)

| Element | Permission | Type |
|---------|-----------|------|
| Customers tab | Module: `CUSTOMERS` | Tab hide |
| View list | `CUSTOMERS_VIEW` | Screen gate |
| Create (FAB) | `CUSTOMERS_CREATE` | FAB hide |
| Edit button | `CUSTOMERS_EDIT` | Button disable |

## Default Role Assignments

### Owner
All permissions (bypass).

### Manager
```
DASHBOARD_VIEW, DASHBOARD_VIEW_SALES, DASHBOARD_VIEW_TRANSACTIONS,
POS_VIEW_PRODUCTS, POS_CREATE_SALE, POS_CREDIT_SALE, POS_VIEW_SALES, POS_VIEW_RECEIPTS,
INVENTORY_VIEW,
INVENTORY_PO_VIEW, INVENTORY_PO_CREATE, INVENTORY_PO_APPROVE, INVENTORY_PO_RECEIVE, INVENTORY_PO_ADD_ITEM,
INVENTORY_TRANSFER_VIEW, INVENTORY_TRANSFER_CREATE, INVENTORY_TRANSFER_DISPATCH,
INVENTORY_TRANSFER_RECEIVE, INVENTORY_TRANSFER_ADD_ITEM,
INVENTORY_ADJUSTMENT_VIEW, INVENTORY_ADJUSTMENT_CREATE, INVENTORY_ADJUSTMENT_APPROVE,
INVENTORY_ADJUSTMENT_ADD_ITEM,
REPORTS_VIEW, REPORTS_STOCK_LEVELS, REPORTS_STOCK_MOVEMENTS, REPORTS_INVENTORY_VALUATION,
REPORTS_PURCHASE_ORDERS, REPORTS_STOCK_TRANSFERS, REPORTS_DEMAND_FORECASTING,
REPORTS_PROFITABILITY, REPORTS_COMPLIANCE_AUDIT,
CUSTOMERS_VIEW, CUSTOMERS_CREATE, CUSTOMERS_EDIT,
SETTINGS_VIEW, SETTINGS_MANAGE
```

### Cashier
```
DASHBOARD_VIEW,
POS_VIEW_PRODUCTS, POS_CREATE_SALE, POS_VIEW_SALES, POS_VIEW_RECEIPTS
```

### Warehouse Staff
```
DASHBOARD_VIEW,
INVENTORY_VIEW,
INVENTORY_PO_VIEW, INVENTORY_PO_ADD_ITEM,
INVENTORY_TRANSFER_VIEW, INVENTORY_TRANSFER_CREATE, INVENTORY_TRANSFER_DISPATCH,
INVENTORY_TRANSFER_RECEIVE, INVENTORY_TRANSFER_ADD_ITEM,
INVENTORY_ADJUSTMENT_VIEW, INVENTORY_ADJUSTMENT_CREATE, INVENTORY_ADJUSTMENT_ADD_ITEM,
REPORTS_VIEW, REPORTS_STOCK_LEVELS, REPORTS_STOCK_MOVEMENTS
```

### Accountant
```
DASHBOARD_VIEW, DASHBOARD_VIEW_SALES, DASHBOARD_VIEW_TRANSACTIONS,
INVENTORY_VIEW, INVENTORY_PO_VIEW,
REPORTS_VIEW, REPORTS_STOCK_LEVELS, REPORTS_STOCK_MOVEMENTS,
REPORTS_INVENTORY_VALUATION, REPORTS_PURCHASE_ORDERS, REPORTS_STOCK_TRANSFERS,
REPORTS_PROFITABILITY, REPORTS_COMPLIANCE_AUDIT
```

### Viewer (Read-Only)
```
DASHBOARD_VIEW
```

## Permission Code Reference (37 codes)

| Code | Module | Description |
|------|--------|-------------|
| `DASHBOARD_VIEW` | DASHBOARD | View dashboard KPIs |
| `DASHBOARD_VIEW_SALES` | DASHBOARD | View today's sales section |
| `DASHBOARD_VIEW_TRANSACTIONS` | DASHBOARD | View recent transactions |
| `POS_VIEW_PRODUCTS` | POS | View product grid |
| `POS_CREATE_SALE` | POS | Create cash sales |
| `POS_CREDIT_SALE` | POS | Create credit sales |
| `POS_VIEW_SALES` | POS | View sales history |
| `POS_VIEW_RECEIPTS` | POS | View/print receipts |
| `POS_VOID_SALE` | POS | Void existing sales |
| `INVENTORY_VIEW` | INVENTORY | View stock levels |
| `INVENTORY_PO_VIEW` | INVENTORY | View purchase orders |
| `INVENTORY_PO_CREATE` | INVENTORY | Create purchase orders |
| `INVENTORY_PO_APPROVE` | INVENTORY | Approve purchase orders |
| `INVENTORY_PO_RECEIVE` | INVENTORY | Receive purchase orders |
| `INVENTORY_PO_ADD_ITEM` | INVENTORY | Add items to POs |
| `INVENTORY_TRANSFER_VIEW` | INVENTORY | View stock transfers |
| `INVENTORY_TRANSFER_CREATE` | INVENTORY | Create stock transfers |
| `INVENTORY_TRANSFER_DISPATCH` | INVENTORY | Dispatch transfers |
| `INVENTORY_TRANSFER_RECEIVE` | INVENTORY | Receive transfers |
| `INVENTORY_TRANSFER_ADD_ITEM` | INVENTORY | Add items to transfers |
| `INVENTORY_ADJUSTMENT_VIEW` | INVENTORY | View stock adjustments |
| `INVENTORY_ADJUSTMENT_CREATE` | INVENTORY | Create stock adjustments |
| `INVENTORY_ADJUSTMENT_APPROVE` | INVENTORY | Approve adjustments |
| `INVENTORY_ADJUSTMENT_ADD_ITEM` | INVENTORY | Add items to adjustments |
| `REPORTS_VIEW` | REPORTS | Access reports section |
| `REPORTS_STOCK_LEVELS` | REPORTS | Stock levels report |
| `REPORTS_STOCK_MOVEMENTS` | REPORTS | Stock movements report |
| `REPORTS_INVENTORY_VALUATION` | REPORTS | Inventory valuation report |
| `REPORTS_PURCHASE_ORDERS` | REPORTS | Purchase orders report |
| `REPORTS_STOCK_TRANSFERS` | REPORTS | Stock transfers report |
| `REPORTS_DEMAND_FORECASTING` | REPORTS | Demand forecasting report |
| `REPORTS_PROFITABILITY` | REPORTS | Profitability analysis |
| `REPORTS_COMPLIANCE_AUDIT` | REPORTS | Compliance audit report |
| `CUSTOMERS_VIEW` | CUSTOMERS | View customers |
| `CUSTOMERS_CREATE` | CUSTOMERS | Create customers |
| `CUSTOMERS_EDIT` | CUSTOMERS | Edit customers |
| `SETTINGS_VIEW` | SETTINGS | View settings |
| `SETTINGS_MANAGE` | SETTINGS | Manage settings |

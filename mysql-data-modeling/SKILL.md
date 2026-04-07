---
name: mysql-data-modeling
description: "Universal SaaS data modeling patterns from Silverston's Data Model Resource Books. Use when designing database schemas for people/organisations, products, orders, invoicing, HR, or accounting. Covers party model, role-based relationships, product classification hierarchies, order lifecycle, and universal identifier patterns."
---

# Universal Data Modeling Patterns for SaaS (Silverston)

Source: *The Data Model Resource Book* Vol. 1 & 2, Len Silverston.
These are the non-obvious patterns — what most developers get wrong by starting naive.

---

## 1. The Party Model — One Table for All People and Organisations

**Why it fails naive:** Separate `customers`, `employees`, `suppliers` tables. A company that is both a supplier AND a customer ends up in multiple tables with conflicting data.

**Silverston's solution:** `party` is the supertype. `person` and `organisation` are subtypes. Roles live separately.

```sql
CREATE TABLE party (
  party_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  party_type ENUM('PERSON','ORGANISATION') NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE person (
  party_id   INT UNSIGNED PRIMARY KEY,
  first_name VARCHAR(100),
  last_name  VARCHAR(100),
  birth_date DATE,
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);

CREATE TABLE organisation (
  party_id       INT UNSIGNED PRIMARY KEY,
  org_name       VARCHAR(255) NOT NULL,
  federal_tax_id VARCHAR(50),
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);
```

---

## 2. Party Roles — Separating Identity from Function

A party's *type* never changes. Their *roles* change and can be multiple simultaneously.

```sql
CREATE TABLE party_role_type (
  party_role_type_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description        VARCHAR(100) NOT NULL  -- 'CUSTOMER','EMPLOYEE','SUPPLIER','RESELLER'
);

CREATE TABLE party_role (
  party_role_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  party_id           INT UNSIGNED NOT NULL,
  party_role_type_id SMALLINT UNSIGNED NOT NULL,
  from_date          DATE NOT NULL,
  thru_date          DATE NULL,             -- NULL = currently active
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);
```

**Key rule:** Never make `CUSTOMER` a column on `party`. Each role = one `party_role` row. Active roles: `thru_date IS NULL OR thru_date >= CURDATE()`.

---

## 3. Party Relationships — Time-Bounded Connections Between Roles

```sql
CREATE TABLE party_relationship_type (
  party_relationship_type_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description                VARCHAR(100) NOT NULL,  -- 'EMPLOYMENT','CUSTOMER_RELATIONSHIP'
  from_role_type_id          SMALLINT UNSIGNED NOT NULL,
  to_role_type_id            SMALLINT UNSIGNED NOT NULL
);

CREATE TABLE party_relationship (
  from_party_role_id         INT UNSIGNED NOT NULL,
  to_party_role_id           INT UNSIGNED NOT NULL,
  party_relationship_type_id SMALLINT UNSIGNED NOT NULL,
  from_date                  DATE NOT NULL,
  thru_date                  DATE NULL,
  PRIMARY KEY (from_party_role_id, to_party_role_id, party_relationship_type_id, from_date)
);
```

---

## 4. Contact Mechanisms — One Pattern for All Contact Types

```sql
CREATE TABLE contact_mech_type (
  contact_mech_type_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description          VARCHAR(50) NOT NULL  -- 'POSTAL_ADDRESS','EMAIL','PHONE','MOBILE'
);

CREATE TABLE contact_mechanism (
  contact_mech_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  contact_mech_type_id SMALLINT UNSIGNED NOT NULL
);

CREATE TABLE postal_address (
  contact_mech_id INT UNSIGNED PRIMARY KEY,
  address1        VARCHAR(255) NOT NULL,
  city            VARCHAR(100),
  postal_code     VARCHAR(20),
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE telecom_number (
  contact_mech_id INT UNSIGNED PRIMARY KEY,
  country_code    VARCHAR(5),
  phone_number    VARCHAR(20) NOT NULL,
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE electronic_address (
  contact_mech_id INT UNSIGNED PRIMARY KEY,
  email_address   VARCHAR(255),
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE party_contact_mech (
  party_id         INT UNSIGNED NOT NULL,
  contact_mech_id  INT UNSIGNED NOT NULL,
  from_date        DATE NOT NULL,
  thru_date        DATE NULL,
  PRIMARY KEY (party_id, contact_mech_id, from_date)
);

CREATE TABLE contact_mech_purpose (
  party_id         INT UNSIGNED NOT NULL,
  contact_mech_id  INT UNSIGNED NOT NULL,
  purpose_type     VARCHAR(50) NOT NULL,  -- 'BILLING','SHIPPING','PRIMARY'
  from_date        DATE NOT NULL,
  thru_date        DATE NULL,
  PRIMARY KEY (party_id, contact_mech_id, purpose_type, from_date)
);
```

---

## 5. Product Category Hierarchy — Self-Referencing Rollup

```sql
CREATE TABLE product_category (
  product_category_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description         VARCHAR(255) NOT NULL
);

CREATE TABLE product_category_rollup (
  parent_product_category_id INT UNSIGNED NOT NULL,
  child_product_category_id  INT UNSIGNED NOT NULL,
  from_date                  DATE NOT NULL,
  thru_date                  DATE NULL,
  PRIMARY KEY (parent_product_category_id, child_product_category_id, from_date)
);

CREATE TABLE product_category_classification (
  product_id          INT UNSIGNED NOT NULL,
  product_category_id INT UNSIGNED NOT NULL,
  from_date           DATE NOT NULL,
  thru_date           DATE NULL,
  primary_flag        TINYINT(1) DEFAULT 0,  -- avoids double-counting in reports
  PRIMARY KEY (product_id, product_category_id, from_date)
);
```

---

## 6. Product Identification — Multiple Codes Per Product

```sql
CREATE TABLE good_identification_type (
  id_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description VARCHAR(50) NOT NULL  -- 'UPC_A','ISBN','SKU','MANUFACTURER_ID','ASIN'
);

CREATE TABLE good_identification (
  product_id INT UNSIGNED NOT NULL,
  id_type_id SMALLINT UNSIGNED NOT NULL,
  id_value   VARCHAR(100) NOT NULL,
  PRIMARY KEY (product_id, id_type_id)
);
```

---

## 7. Product Features — Variants Without Variant Tables

```sql
CREATE TABLE product_feature_type (
  feature_type_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description     VARCHAR(50) NOT NULL  -- 'COLOR','SIZE','BILLING_CYCLE'
);

CREATE TABLE product_feature (
  product_feature_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  feature_type_id    SMALLINT UNSIGNED NOT NULL,
  description        VARCHAR(100) NOT NULL  -- 'Red','XL','Annual','Monthly'
);

CREATE TABLE product_feature_applicability (
  product_id         INT UNSIGNED NOT NULL,
  product_feature_id INT UNSIGNED NOT NULL,
  applicability_type ENUM('REQUIRED','STANDARD','OPTIONAL','SELECTABLE') NOT NULL,
  from_date          DATE NOT NULL,
  thru_date          DATE NULL,
  PRIMARY KEY (product_id, product_feature_id, from_date)
);
```

---

## 8. Price Components — Never Hardcode Price on Product

```sql
CREATE TABLE price_component (
  price_component_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  price_component_type_id  SMALLINT UNSIGNED NOT NULL,
  product_id               INT UNSIGNED,
  from_date                DATE NOT NULL,
  thru_date                DATE NULL,
  price                    DECIMAL(14,4),
  percent                  DECIMAL(7,4),
  geo_id                   INT UNSIGNED,
  party_type_id            SMALLINT UNSIGNED,
  quantity_break_id        INT UNSIGNED,
  currency_uom_id          SMALLINT UNSIGNED
);
```

**SaaS example:** Base price row for a plan + `PROMOTIONAL_DISCOUNT` row with `percent = 20` and `thru_date = '2025-12-31'`. No code changes needed for time-limited offers.

---

## 9. Order Model — Header + Items + Roles

```sql
CREATE TABLE order_header (
  order_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_type ENUM('SALES_ORDER','PURCHASE_ORDER') NOT NULL,
  order_date DATE NOT NULL,
  entry_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_item (
  order_id          INT UNSIGNED NOT NULL,
  order_item_seq_id SMALLINT UNSIGNED NOT NULL,
  product_id        INT UNSIGNED NOT NULL,
  quantity          DECIMAL(12,3),
  unit_price        DECIMAL(14,4),  -- locked at order time; NOT derived from product
  PRIMARY KEY (order_id, order_item_seq_id)
);

CREATE TABLE order_role (
  order_id           INT UNSIGNED NOT NULL,
  party_id           INT UNSIGNED NOT NULL,
  order_role_type_id SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (order_id, party_id, order_role_type_id)
);
-- order_role_type descriptions: 'PLACING_PARTY','BILL_TO_CUSTOMER','SHIP_TO_PARTY','SALES_REP'
```

---

## 10. Order Adjustments — Discounts and Taxes as Rows

```sql
CREATE TABLE order_adjustment (
  order_adjustment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id            INT UNSIGNED NOT NULL,
  order_item_seq_id   SMALLINT UNSIGNED NULL,  -- NULL = applies to whole order
  adjustment_type_id  SMALLINT UNSIGNED NOT NULL,
  amount              DECIMAL(14,4),
  percentage          DECIMAL(7,4),
  geo_id              INT UNSIGNED
);
-- adjustment_type descriptions: 'DISCOUNT','SHIPPING_CHARGE','SALES_TAX','PROCESSING_FEE'
```

---

## 11. Invoice Structure and Partial Billing

**Key insight:** An invoice is NOT a copy of an order. One order → multiple invoices (partial shipments). `order_item_billing` is the bridge.

```sql
CREATE TABLE invoice (
  invoice_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  invoice_date DATE NOT NULL,
  message      VARCHAR(255)  -- appears on printed invoice
);

CREATE TABLE invoice_item (
  invoice_id        INT UNSIGNED NOT NULL,
  invoice_item_seq  SMALLINT UNSIGNED NOT NULL,
  invoice_item_type ENUM('PRODUCT','ADJUSTMENT','FEATURE') NOT NULL,
  product_id        INT UNSIGNED,
  quantity          DECIMAL(12,3),
  amount            DECIMAL(14,4),
  taxable_flag      TINYINT(1) DEFAULT 1,
  PRIMARY KEY (invoice_id, invoice_item_seq)
);

-- Bridge: supports partial billing and multi-order invoices
CREATE TABLE order_item_billing (
  order_id          INT UNSIGNED NOT NULL,
  order_item_seq_id SMALLINT UNSIGNED NOT NULL,
  invoice_id        INT UNSIGNED NOT NULL,
  invoice_item_seq  SMALLINT UNSIGNED NOT NULL,
  quantity          DECIMAL(12,3),
  amount            DECIMAL(14,4),
  PRIMARY KEY (order_id, order_item_seq_id, invoice_id, invoice_item_seq)
);
```

---

## 12. Payment Application — Partial Payments and Overpayments

```sql
CREATE TABLE payment (
  payment_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  payment_type        ENUM('RECEIPT','DISBURSEMENT') NOT NULL,
  payment_method_type VARCHAR(30),  -- 'CASH','STRIPE','ACH'
  effective_date      DATE NOT NULL,
  amount              DECIMAL(14,4) NOT NULL,
  status              ENUM('RECEIVED','APPLIED','VOID','REFUNDED') DEFAULT 'RECEIVED'
);

CREATE TABLE payment_application (
  payment_application_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  payment_id             INT UNSIGNED NOT NULL,
  invoice_id             INT UNSIGNED,       -- NULL = unapplied advance payment
  invoice_item_seq       SMALLINT UNSIGNED,
  amount_applied         DECIMAL(14,4) NOT NULL
);
```

---

## Summary: The Core Anti-Pattern Map

| What devs build | What Silverston uses |
|---|---|
| `customers` + `employees` tables | `party` + `party_role` |
| `customer.is_supplier` column | Two `party_role` rows |
| `product.price` column | `price_component` with date range |
| `order.tax`, `order.discount` columns | `order_adjustment` rows |
| `order.customer_id` column | `order_role` with type |
| `invoice.total` column | Sum of `invoice_item` rows |
| Payment settles one invoice | `payment_application` many-to-many |
| `product.category_id` column | `product_category_rollup` hierarchy |

---

*Source: Silverston, The Data Model Resource Book Vol. 1 (Ch. 2, 3, 4, 7, 8, 9)*

---
name: mysql-data-modeling
description: "Universal SaaS data modeling patterns from Silverston's Data Model Resource Books. Use when designing database schemas for people/organisations, products, orders, invoicing, HR, or accounting. Covers party model, role-based relationships, product classification hierarchies, order lifecycle, and universal identifier patterns."
---

# Universal Data Modeling Patterns for SaaS (Silverston)

Source: *The Data Model Resource Book* Vol. 1 & 2, Len Silverston.
These are the non-obvious patterns — what most developers get wrong by starting naive.

---

## 1. The Party Model — One Table for All People and Organisations

**Naive approach:** Separate `customers`, `employees`, `suppliers`, `contacts` tables with duplicated address/phone columns everywhere.

**Why it fails:** A company can be both a supplier AND a customer. An employee can also be a client. You end up with the same real-world entity stored in 3 tables with conflicting data.

**Silverston's solution:** `party` is the supertype. `person` and `organisation` are subtypes. Roles live in a separate table.

```sql
CREATE TABLE party (
  party_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  party_type   ENUM('PERSON','ORGANISATION') NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE person (
  party_id          INT UNSIGNED PRIMARY KEY,
  first_name        VARCHAR(100),
  last_name         VARCHAR(100),
  birth_date        DATE,
  gender            CHAR(1),
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);

CREATE TABLE organisation (
  party_id       INT UNSIGNED PRIMARY KEY,
  org_name       VARCHAR(255) NOT NULL,
  federal_tax_id VARCHAR(50),
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);
```

**SaaS example:** A B2B SaaS where `Acme Ltd` is both a paying client and a reseller. One row in `party`, two rows in `party_role`.

---

## 2. Party Roles — Separating Identity from Function

**The non-obvious insight:** A party's *type* (Person vs Organisation) never changes. Their *roles* change constantly and can be multiple simultaneously.

```sql
CREATE TABLE party_role_type (
  party_role_type_id   SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description          VARCHAR(100) NOT NULL  -- 'CUSTOMER','EMPLOYEE','SUPPLIER','RESELLER','PROSPECT'
);

CREATE TABLE party_role (
  party_role_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  party_id             INT UNSIGNED NOT NULL,
  party_role_type_id   SMALLINT UNSIGNED NOT NULL,
  from_date            DATE NOT NULL,
  thru_date            DATE NULL,           -- NULL = currently active
  FOREIGN KEY (party_id) REFERENCES party(party_id),
  FOREIGN KEY (party_role_type_id) REFERENCES party_role_type(party_role_type_id)
);
```

**Key rule:** Never make `CUSTOMER` a column on `party`. The same party gets a `party_role` row for each role they play. Query active roles with `thru_date IS NULL OR thru_date >= CURDATE()`.

---

## 3. Party Relationships — Time-Bounded Connections Between Roles

**What most devs miss:** Relationships are between *roles*, not between parties directly. And all relationships have a lifespan.

```sql
CREATE TABLE party_relationship_type (
  party_relationship_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description                 VARCHAR(100) NOT NULL,  -- 'EMPLOYMENT','CUSTOMER_RELATIONSHIP','RESELLER_AGREEMENT'
  from_role_type_id           SMALLINT UNSIGNED NOT NULL,  -- role this rel goes FROM
  to_role_type_id             SMALLINT UNSIGNED NOT NULL,  -- role this rel goes TO
  FOREIGN KEY (from_role_type_id) REFERENCES party_role_type(party_role_type_id),
  FOREIGN KEY (to_role_type_id)   REFERENCES party_role_type(party_role_type_id)
);

CREATE TABLE party_relationship (
  from_party_role_id          INT UNSIGNED NOT NULL,
  to_party_role_id            INT UNSIGNED NOT NULL,
  party_relationship_type_id  SMALLINT UNSIGNED NOT NULL,
  from_date                   DATE NOT NULL,
  thru_date                   DATE NULL,
  status_type_id              SMALLINT UNSIGNED,  -- 'ACTIVE','INACTIVE','PENDING'
  comment                     TEXT,
  PRIMARY KEY (from_party_role_id, to_party_role_id, party_relationship_type_id, from_date),
  FOREIGN KEY (from_party_role_id) REFERENCES party_role(party_role_id),
  FOREIGN KEY (to_party_role_id)   REFERENCES party_role(party_role_id)
);
```

**SaaS example:** `John Smith (EMPLOYEE role) → ABC Corp (EMPLOYER role)` with `from_date = 2020-01-01`, `thru_date = NULL`. Same John Smith can have a `CUSTOMER` role linked to a different organisation via another relationship row.

---

## 4. Contact Mechanisms — One Pattern for All Contact Types

**Naive approach:** `customer.email`, `customer.phone`, `customer.address` columns. Falls apart when a company has 5 phone numbers, 3 addresses, 2 emails.

**Silverston's solution:** `contact_mechanism` is a supertype. All contact types are subtypes. Junction table links parties to their mechanisms with purpose and date range.

```sql
CREATE TABLE contact_mech_type (
  contact_mech_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description           VARCHAR(50) NOT NULL  -- 'POSTAL_ADDRESS','EMAIL','PHONE','MOBILE','FAX','WEB_URL'
);

CREATE TABLE contact_mechanism (
  contact_mech_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  contact_mech_type_id  SMALLINT UNSIGNED NOT NULL,
  FOREIGN KEY (contact_mech_type_id) REFERENCES contact_mech_type(contact_mech_type_id)
);

CREATE TABLE postal_address (
  contact_mech_id  INT UNSIGNED PRIMARY KEY,
  address1         VARCHAR(255) NOT NULL,
  address2         VARCHAR(255),
  city             VARCHAR(100),
  postal_code      VARCHAR(20),
  geo_id           INT UNSIGNED,            -- FK to geographic_boundary
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE telecom_number (
  contact_mech_id  INT UNSIGNED PRIMARY KEY,
  country_code     VARCHAR(5),
  area_code        VARCHAR(10),
  phone_number     VARCHAR(20) NOT NULL,
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE electronic_address (
  contact_mech_id  INT UNSIGNED PRIMARY KEY,
  email_address    VARCHAR(255),
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE party_contact_mech (
  party_id              INT UNSIGNED NOT NULL,
  contact_mech_id       INT UNSIGNED NOT NULL,
  contact_mech_type_id  SMALLINT UNSIGNED NOT NULL,
  from_date             DATE NOT NULL,
  thru_date             DATE NULL,
  non_solicitation_ind  TINYINT(1) DEFAULT 0,
  extension             VARCHAR(10),
  PRIMARY KEY (party_id, contact_mech_id, from_date),
  FOREIGN KEY (party_id)        REFERENCES party(party_id),
  FOREIGN KEY (contact_mech_id) REFERENCES contact_mechanism(contact_mech_id)
);

CREATE TABLE contact_mech_purpose (
  party_id              INT UNSIGNED NOT NULL,
  contact_mech_id       INT UNSIGNED NOT NULL,
  purpose_type          VARCHAR(50) NOT NULL,  -- 'BILLING','SHIPPING','PRIMARY','SUPPORT'
  from_date             DATE NOT NULL,
  thru_date             DATE NULL,
  PRIMARY KEY (party_id, contact_mech_id, purpose_type, from_date)
);
```

---

## 5. Geographic Structure — Unlimited Depth Hierarchy

**Pattern:** Self-referencing `geographic_boundary` with type, not separate `country`, `state`, `city` tables.

```sql
CREATE TABLE geographic_boundary (
  geo_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  geo_type      ENUM('COUNTRY','STATE','PROVINCE','COUNTY','CITY','POSTAL_CODE') NOT NULL,
  name          VARCHAR(100) NOT NULL,
  abbreviation  VARCHAR(10),
  parent_geo_id INT UNSIGNED NULL,          -- recursive: city within state within country
  FOREIGN KEY (parent_geo_id) REFERENCES geographic_boundary(geo_id)
);
```

---

## 6. Product Category Hierarchy — Self-Referencing Rollup

**Naive approach:** A `category_id` column on `product`. Breaks when you need multi-level: Electronics > Computers > Laptops > Gaming Laptops.

**Silverston's solution:** `product_category_rollup` resolves many-to-many hierarchy with unlimited depth.

```sql
CREATE TABLE product_category (
  product_category_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description          VARCHAR(255) NOT NULL
);

CREATE TABLE product_category_rollup (
  parent_product_category_id  INT UNSIGNED NOT NULL,
  child_product_category_id   INT UNSIGNED NOT NULL,
  from_date                   DATE NOT NULL,
  thru_date                   DATE NULL,
  PRIMARY KEY (parent_product_category_id, child_product_category_id, from_date),
  FOREIGN KEY (parent_product_category_id) REFERENCES product_category(product_category_id),
  FOREIGN KEY (child_product_category_id)  REFERENCES product_category(product_category_id)
);

-- One product can belong to multiple categories
CREATE TABLE product_category_classification (
  product_id           INT UNSIGNED NOT NULL,
  product_category_id  INT UNSIGNED NOT NULL,
  from_date            DATE NOT NULL,
  thru_date            DATE NULL,
  primary_flag         TINYINT(1) DEFAULT 0,  -- avoids double-counting in reports
  PRIMARY KEY (product_id, product_category_id, from_date)
);
```

---

## 7. Product Identification — Multiple Codes Per Product

**The insight:** A single product can have a UPC, an internal SKU, a manufacturer code, and an ISBN simultaneously. Never put these as separate columns.

```sql
CREATE TABLE good_identification_type (
  id_type_id   SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description  VARCHAR(50) NOT NULL  -- 'UPC_A','UPC_E','ISBN','SKU','MANUFACTURER_ID','ASIN'
);

CREATE TABLE good_identification (
  product_id   INT UNSIGNED NOT NULL,
  id_type_id   SMALLINT UNSIGNED NOT NULL,
  id_value     VARCHAR(100) NOT NULL,
  PRIMARY KEY (product_id, id_type_id),
  FOREIGN KEY (product_id) REFERENCES product(product_id),
  FOREIGN KEY (id_type_id) REFERENCES good_identification_type(id_type_id)
);
```

---

## 8. Product Features — Variants Without Variant Tables

**Naive approach:** `product_size`, `product_color`, `product_material` columns. Or worse: a separate `product_variant` table that duplicates the product row.

**Silverston's solution:** `product_feature` with a type, linked to products via `product_feature_applicability`.

```sql
CREATE TABLE product_feature_type (
  feature_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description      VARCHAR(50) NOT NULL  -- 'COLOR','SIZE','DIMENSION','BRAND','BILLING_CYCLE'
);

CREATE TABLE product_feature (
  product_feature_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  feature_type_id     SMALLINT UNSIGNED NOT NULL,
  description         VARCHAR(100) NOT NULL,  -- 'Red','XL','Annual','Monthly'
  FOREIGN KEY (feature_type_id) REFERENCES product_feature_type(feature_type_id)
);

CREATE TABLE product_feature_applicability (
  product_id          INT UNSIGNED NOT NULL,
  product_feature_id  INT UNSIGNED NOT NULL,
  applicability_type  ENUM('REQUIRED','STANDARD','OPTIONAL','SELECTABLE') NOT NULL,
  from_date           DATE NOT NULL,
  thru_date           DATE NULL,
  PRIMARY KEY (product_id, product_feature_id, from_date)
);
```

**SaaS example:** A SaaS plan product has `BILLING_CYCLE` feature with values `Monthly` and `Annual`, both `SELECTABLE`. No separate plan rows needed.

---

## 9. Price Components — Never Hardcode Price on Product

**What most devs get wrong:** `product.price DECIMAL(10,2)`. This breaks the moment you need quantity breaks, geographic pricing, promotional discounts, or customer-tier pricing.

**Silverston's solution:** `price_component` with type, date range, and optional linkage to geography, party type, and quantity breaks.

```sql
CREATE TABLE price_component_type (
  price_component_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description              VARCHAR(50) NOT NULL
  -- 'BASE_PRICE','QUANTITY_BREAK','PROMOTIONAL_DISCOUNT','SURCHARGE','MSRP','RECURRING_CHARGE'
);

CREATE TABLE quantity_break (
  quantity_break_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  from_quantity      DECIMAL(12,2) NOT NULL,
  thru_quantity      DECIMAL(12,2)           -- NULL = no upper limit
);

CREATE TABLE price_component (
  price_component_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  price_component_type_id  SMALLINT UNSIGNED NOT NULL,
  product_id               INT UNSIGNED,       -- NULL if applies to a feature
  product_feature_id       INT UNSIGNED,
  from_date                DATE NOT NULL,
  thru_date                DATE NULL,
  price                    DECIMAL(14,4),      -- absolute amount, OR
  percent                  DECIMAL(7,4),       -- percentage discount/surcharge
  geo_id                   INT UNSIGNED,       -- optional: region-specific price
  party_type_id            SMALLINT UNSIGNED,  -- optional: customer-type price
  quantity_break_id        INT UNSIGNED,       -- optional: volume pricing
  currency_uom_id          SMALLINT UNSIGNED,  -- optional: multi-currency
  comment                  VARCHAR(255),
  FOREIGN KEY (price_component_type_id) REFERENCES price_component_type(price_component_type_id)
);
```

**SaaS example:** Base price row for a plan, then a `PROMOTIONAL_DISCOUNT` row with `percent = 20` and `thru_date = '2025-12-31'` for a Black Friday deal. No code changes needed.

---

## 10. Order Model — Header + Items + Roles

**The non-obvious pattern:** Orders should not have `customer_id`, `supplier_id` directly. They use `order_role` with a type, so any number of parties can participate.

```sql
CREATE TABLE order_header (
  order_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_type  ENUM('SALES_ORDER','PURCHASE_ORDER') NOT NULL,
  order_date  DATE NOT NULL,
  entry_date  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status_id   SMALLINT UNSIGNED
);

CREATE TABLE order_item (
  order_id               INT UNSIGNED NOT NULL,
  order_item_seq_id      SMALLINT UNSIGNED NOT NULL,
  product_id             INT UNSIGNED NOT NULL,
  quantity               DECIMAL(12,3),
  unit_price             DECIMAL(14,4),    -- captured at order time; NOT derived from product
  estimated_ship_date    DATE,
  shipping_instructions  TEXT,
  item_description       VARCHAR(255),
  PRIMARY KEY (order_id, order_item_seq_id),
  FOREIGN KEY (order_id) REFERENCES order_header(order_id)
);

CREATE TABLE order_role_type (
  order_role_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description         VARCHAR(50) NOT NULL
  -- 'PLACING_PARTY','BILL_TO_CUSTOMER','SHIP_TO_PARTY','INTERNAL_ORG','SALES_REP'
);

CREATE TABLE order_role (
  order_id            INT UNSIGNED NOT NULL,
  party_id            INT UNSIGNED NOT NULL,
  order_role_type_id  SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (order_id, party_id, order_role_type_id),
  FOREIGN KEY (order_id) REFERENCES order_header(order_id),
  FOREIGN KEY (party_id) REFERENCES party(party_id)
);
```

**Why `unit_price` is NOT derived:** Price components reflect catalogue pricing at a point in time. Once an order is placed, the agreed price is locked. These can diverge after a price change.

---

## 11. Order Adjustments — Discounts and Taxes as Rows, Not Columns

**Naive approach:** `order.discount_amount`, `order.tax_amount`, `order.shipping_charge`. You add a new adjustment type by altering the table.

```sql
CREATE TABLE order_adjustment_type (
  adjustment_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description         VARCHAR(50) NOT NULL
  -- 'DISCOUNT','SURCHARGE','SHIPPING_CHARGE','SALES_TAX','PROCESSING_FEE'
);

CREATE TABLE order_adjustment (
  order_adjustment_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id             INT UNSIGNED NOT NULL,
  order_item_seq_id    SMALLINT UNSIGNED NULL,   -- NULL = applies to whole order
  adjustment_type_id   SMALLINT UNSIGNED NOT NULL,
  amount               DECIMAL(14,4),
  percentage           DECIMAL(7,4),
  geo_id               INT UNSIGNED,             -- for geo-specific tax lookup
  FOREIGN KEY (order_id) REFERENCES order_header(order_id)
);
```

---

## 12. Invoice Structure and Partial Billing

**Key insight:** An invoice is NOT a copy of an order. One order can produce multiple invoices over time (partial shipments). One invoice can cover multiple orders. The `order_item_billing` bridge table is the join.

```sql
CREATE TABLE invoice (
  invoice_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  invoice_date  DATE NOT NULL,
  description   VARCHAR(255),
  message       VARCHAR(255)   -- appears on the printed invoice
);

CREATE TABLE invoice_item (
  invoice_id         INT UNSIGNED NOT NULL,
  invoice_item_seq   SMALLINT UNSIGNED NOT NULL,
  invoice_item_type  ENUM('PRODUCT','ADJUSTMENT','WORK_EFFORT','FEATURE') NOT NULL,
  product_id         INT UNSIGNED,
  quantity           DECIMAL(12,3),
  amount             DECIMAL(14,4),
  taxable_flag       TINYINT(1) DEFAULT 1,
  item_description   VARCHAR(255),
  PRIMARY KEY (invoice_id, invoice_item_seq),
  FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
);

-- This bridge is the secret: it supports partial billing and multi-order invoices
CREATE TABLE order_item_billing (
  order_id           INT UNSIGNED NOT NULL,
  order_item_seq_id  SMALLINT UNSIGNED NOT NULL,
  invoice_id         INT UNSIGNED NOT NULL,
  invoice_item_seq   SMALLINT UNSIGNED NOT NULL,
  quantity           DECIMAL(12,3),
  amount             DECIMAL(14,4),
  PRIMARY KEY (order_id, order_item_seq_id, invoice_id, invoice_item_seq)
);
```

---

## 13. Payment Application — Partial Payments and Overpayments

**What most devs miss:** A payment doesn't always fully settle one invoice. It can be partial, or cover multiple invoices. The `payment_application` table handles all of this.

```sql
CREATE TABLE payment (
  payment_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  payment_type        ENUM('RECEIPT','DISBURSEMENT') NOT NULL,
  payment_method_type VARCHAR(30),   -- 'CASH','CHECK','CREDIT_CARD','ACH','STRIPE'
  effective_date      DATE NOT NULL,
  payment_ref_num     VARCHAR(100),
  amount              DECIMAL(14,4) NOT NULL,
  status              ENUM('RECEIVED','APPLIED','VOID','REFUNDED') DEFAULT 'RECEIVED',
  from_party_id       INT UNSIGNED,
  to_party_id         INT UNSIGNED
);

CREATE TABLE payment_application (
  payment_application_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  payment_id              INT UNSIGNED NOT NULL,
  invoice_id              INT UNSIGNED,         -- NULL = unapplied advance payment
  invoice_item_seq        SMALLINT UNSIGNED,    -- NULL = applied to whole invoice
  billing_account_id      INT UNSIGNED,
  amount_applied          DECIMAL(14,4) NOT NULL,
  FOREIGN KEY (payment_id) REFERENCES payment(payment_id),
  FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
);
```

**SaaS example:** A customer pays $500 against a $300 invoice. `payment.amount = 500`, two `payment_application` rows: one for $300 against the invoice, one for $200 as an unapplied credit (no `invoice_id`).

---

## 14. HR: Position vs Employment (The Job Slot Pattern)

**What most devs model:** `employee.department_id`, `employee.job_title`, `employee.manager_id`.

**What Silverston shows:** A `position` is the *job slot* (authorised headcount). `employment` is the person-in-slot. This lets you track org structure independently of who fills it.

```sql
CREATE TABLE position_type (
  position_type_id  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  title             VARCHAR(100) NOT NULL,  -- 'Senior Engineer','Account Manager'
  description       TEXT,
  benefit_percent   DECIMAL(5,2),
  salary_flag       TINYINT(1) DEFAULT 1,
  fulltime_flag     TINYINT(1) DEFAULT 1
);

CREATE TABLE position (
  position_id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  position_type_id     INT UNSIGNED,
  budget_item_id       INT UNSIGNED,    -- links to budget authorisation
  estimated_from_date  DATE,
  estimated_thru_date  DATE,
  actual_from_date     DATE,
  actual_thru_date     DATE,
  temporary_flag       TINYINT(1) DEFAULT 0,
  FOREIGN KEY (position_type_id) REFERENCES position_type(position_type_id)
);

-- Many-to-many with history: one person can fill multiple positions over time
CREATE TABLE position_fulfillment (
  position_id  INT UNSIGNED NOT NULL,
  party_id     INT UNSIGNED NOT NULL,
  from_date    DATE NOT NULL,
  thru_date    DATE NULL,
  comment      TEXT,
  PRIMARY KEY (position_id, party_id, from_date)
);

-- Org chart is modelled on positions, not people
CREATE TABLE position_reporting_structure (
  reporting_to_position_id  INT UNSIGNED NOT NULL,
  managed_by_position_id    INT UNSIGNED NOT NULL,
  from_date                 DATE NOT NULL,
  thru_date                 DATE NULL,
  primary_flag              TINYINT(1) DEFAULT 1,  -- for matrix management
  PRIMARY KEY (reporting_to_position_id, managed_by_position_id, from_date)
);

-- Employment IS a party_relationship subtype
CREATE TABLE employment (
  from_party_role_id  INT UNSIGNED NOT NULL,  -- EMPLOYEE role
  to_party_role_id    INT UNSIGNED NOT NULL,  -- INTERNAL_ORGANISATION role
  from_date           DATE NOT NULL,
  thru_date           DATE NULL,
  termination_type_id SMALLINT UNSIGNED NULL,
  PRIMARY KEY (from_party_role_id, to_party_role_id, from_date)
);
```

---

## 15. GL Accounting: Chart of Accounts + Double-Entry Transactions

**Silverston's pattern:** `gl_account` defines the chart. `organisation_gl_account` assigns accounts to specific internal orgs with date ranges. `acctg_trans` is the business event. `acctg_trans_entry` enforces double-entry (debits = credits).

```sql
CREATE TABLE gl_account_type (
  gl_account_type_id  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  description         VARCHAR(50) NOT NULL  -- 'ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE'
);

CREATE TABLE gl_account (
  gl_account_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  gl_account_type_id  SMALLINT UNSIGNED NOT NULL,
  account_name        VARCHAR(100) NOT NULL,
  description         TEXT,
  FOREIGN KEY (gl_account_type_id) REFERENCES gl_account_type(gl_account_type_id)
);

-- Assigns GL accounts to specific business units with validity dates
CREATE TABLE organisation_gl_account (
  internal_organisation_id  INT UNSIGNED NOT NULL,  -- party_id of the org
  gl_account_id             INT UNSIGNED NOT NULL,
  from_date                 DATE NOT NULL,
  thru_date                 DATE NULL,
  PRIMARY KEY (internal_organisation_id, gl_account_id, from_date)
);

CREATE TABLE acctg_trans (
  acctg_trans_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  trans_type        VARCHAR(50) NOT NULL,  -- 'INVOICE','PAYMENT','DEPRECIATION','PAYROLL'
  transaction_date  DATE NOT NULL,
  entry_date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  description       VARCHAR(255),
  -- Optional: link back to originating business transaction
  invoice_id        INT UNSIGNED NULL,
  payment_id        INT UNSIGNED NULL,
  order_id          INT UNSIGNED NULL
);

-- Each transaction has 2+ entries; debits must equal credits
CREATE TABLE acctg_trans_entry (
  acctg_trans_id              INT UNSIGNED NOT NULL,
  acctg_trans_entry_seq_id    SMALLINT UNSIGNED NOT NULL,
  gl_account_id               INT UNSIGNED NOT NULL,
  internal_organisation_id    INT UNSIGNED NOT NULL,
  debit_credit_flag           ENUM('D','C') NOT NULL,   -- D=Debit, C=Credit
  amount                      DECIMAL(15,4) NOT NULL,
  description                 VARCHAR(255),
  PRIMARY KEY (acctg_trans_id, acctg_trans_entry_seq_id),
  FOREIGN KEY (acctg_trans_id) REFERENCES acctg_trans(acctg_trans_id),
  FOREIGN KEY (gl_account_id)  REFERENCES gl_account(gl_account_id)
);
```

**Example:** Invoicing a customer for $900 creates one `acctg_trans` row and two `acctg_trans_entry` rows: Debit `Accounts Receivable $900`, Credit `Revenue $900`. The model is self-enforcing.

---

## Summary: The Core Anti-Pattern Map

| What devs build          | What Silverston uses               |
|--------------------------|------------------------------------|
| `customers` + `employees` tables | `party` + `party_role`    |
| `customer.is_supplier`   | Two `party_role` rows              |
| `product.price`          | `price_component` with date range  |
| `order.tax`, `order.discount` | `order_adjustment` rows       |
| `order.customer_id`      | `order_role` with type             |
| `employee.department_id` | `position_fulfillment` + `position_reporting_structure` |
| `invoice.total`          | Sum of `invoice_item` rows         |
| Hardcoded account types  | `gl_account_type` reference table  |
| Payment settles one invoice | `payment_application` many-to-many |
| `product.category_id`    | `product_category_rollup` hierarchy |

---

*Line count: ~490 | Source: Silverston, The Data Model Resource Book Vol. 1 (Chapters 2, 3, 4, 7, 8, 9)*

# Domain Modeling

Use these prompts to keep SaaS and ERP systems structurally sound.

## Core Questions

- What are the irreversible business events?
- What must be approved before it is committed?
- What must be reversible later?
- What needs an audit trail?
- What varies by tenant through policy instead of code?

## Core Entity Families

- Parties: customer, supplier, employee, user, tenant
- Products and services
- Locations and warehouses
- Commercial documents: quote, order, invoice, payment
- Operational documents: requisition, receipt, transfer, adjustment
- Financial records: ledger entry, journal, allocation, settlement

## Control Review

- Which actions need separation of duties?
- Which transitions need approval thresholds?
- Which records need period locking?
- Which corrections need reversal instead of edit-in-place?

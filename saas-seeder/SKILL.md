---
name: saas-seeder
description: "Prepare a new SaaS repository from the seeder template: prompt for MySQL credentials, create the database, import database/schema SQL, run the auth/RBAC migration, seed a demo franchise and super user, and verify first login. Use when asked to bootstrap a new SaaS from the template."
---

# SaaS Seeder

Bootstrap a new SaaS repo using the seeder template so a single prompt can prepare the database, seed auth/RBAC, and enable first login.

## When to Use

Use when the user says:
- "Using the seeder-script skill, prepare this repository for [SaaS name]"
- "Seed a new SaaS from this template"
- "Initialize the database for a new SaaS"

## Inputs To Collect

Always prompt for the following before running commands:

- MySQL host
- MySQL port
- MySQL username
- MySQL password
- Database name to create
- Franchise details (code, name, email, telephone, country, timezone, currency)
- Super user details (username, email, password)
- Confirm whether to import database/schema SQL dumps
- Confirm whether to run docs/seeder-template/migration.sql

## Required Files And Paths

- docs/seeder-template/migration.sql
- database/schema (optional SQL dumps for existing tables and procedures)
- public/ as web root
- login/logout files in public (copied from Maduuka)

Use the MySQL CLI path defined in root CLAUDE.md.

## Standard Workflow (Required)

1. Validate MySQL connectivity using provided credentials.
2. Create the database if it does not exist.
3. If database/schema exists, import all .sql files in deterministic order.
   - Use alphabetical ordering to avoid dependency issues.
   - If stored procedures are provided separately, import after tables.
4. Run docs/seeder-template/migration.sql to create auth/RBAC baseline.
5. Seed a demo franchise if tbl_franchises exists in the imported schema.
6. Seed baseline roles and permissions using Maduuka conventions:
   - Super Admin, Manager, Finance, Staff, Distributor, HR, Accountant
7. Seed the default super user using the provided credentials.
8. Provide final verification steps and first login URL.

## Seeding Rules

- super_admin users can have franchise_id = NULL.
- Permission codes must be uppercase with underscores.
- Use bcrypt for password hashes.
- Do not assume any table exists; confirm via schema or SHOW TABLES.

## Database Import Notes

- If database/schema contains partial dumps, only those tables are imported.
- If tbl_franchises does not exist, skip franchise seed and warn the user.
- If any required table is missing, stop and ask how to proceed.

## Example Prompt Pattern

When the user says:
"Using the seeder-script skill, prepare this repository for the Academia Pro - Schools management System"

You must:
- Ask for MySQL credentials and database name
- Ask for franchise/demo tenant details
- Ask for super user credentials
- Confirm schema import and migration run
- Execute the seed workflow in order

## Output Requirements

After completion, report:
- Database created and seeded
- Auth/RBAC tables created
- Franchise/demo tenant created (if applicable)
- Super user created
- First login URL

## References

See:
- references/seeder-template.md

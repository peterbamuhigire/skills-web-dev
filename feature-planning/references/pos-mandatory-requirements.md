# POS & Sales Systems — Mandatory Audit Requirements

**Source:** Extracted from `feature-planning/skill.md` to maintain 500-line compliance.
**Back to:** [Feature Planning Skill](../skill.md)

---

---

## 🔐 Domain-Specific Mandatory Requirements

### POS & Sales Systems (CRITICAL for Audit Compliance)

When planning features for POS, checkout, or sales entry systems, **ALWAYS** include these mandatory controls. These are **non-negotiable audit compliance requirements**.

#### M1: POS Session Locking (Recommendation #2)
**Status:** Mandatory | **Priority:** Critical
**Estimated Effort:** 3 weeks | **Budget:** $3,000

**Required Components:**
1. **Session Start/End Workflow** - Supervisor approval for session start and closure
2. **Database-Level Locks** - Prevent backdated transactions after session closure
3. **Automatic Timeout** - Sessions close after 12 hours of inactivity
4. **Historical Session View** - Sales summary per session with complete audit trail

**Why Mandatory:**
- Prevents backdated transaction manipulation (critical audit finding)
- Core requirement for audit trail integrity and SOX compliance
- Addresses high-risk control gap in revenue management
- Required for external audit sign-off

**Implementation Checklist:**
- [ ] Database table: `pos_sessions` (id, sales_point_id, cashier_id, start_time, end_time, status, supervisor_id)
- [ ] Database trigger: Block invoice creation/modification if session closed
- [ ] API endpoint: `/api/pos/sessions.php` (actions: start, close, view_history)
- [ ] UI component: Session status badge in POS header (OPEN/CLOSED with color coding)
- [ ] UI modal: "Session Closed - No transactions allowed" blocking message
- [ ] Stored procedure: `sp_close_pos_session` with supervisor verification
- [ ] Unit tests: Session state transitions, lock enforcement, timeout logic
- [ ] Integration tests: End-to-end session workflow with supervisor approval

#### M2: Sequential Receipt Control & Gap Detection (Recommendation #6)
**Status:** Mandatory | **Priority:** Critical
**Estimated Effort:** 2 weeks | **Budget:** $2,000
**Depends On:** M1 (POS Session Locking)

**Required Components:**
1. **Automated Gap Detection** - Daily cron job identifies missing receipt numbers
2. **Management Alerts** - Email/SMS notifications for detected gaps
3. **Voided Receipt Tracking** - All voids require justification notes (min 10 chars)
4. **Supervisor Override Workflow** - Gap resolution requires supervisor approval

**Why Mandatory:**
- Critical for revenue leakage prevention (high-priority audit finding)
- External audit sign-off requirement for financial statements
- Detects potential fraud through missing receipt sequences
- Required for compliance with internal control policies

**Implementation Checklist:**
- [ ] Database table: `receipt_sequence_gaps` (id, sales_point_id, missing_numbers, detection_date, status, resolution_notes)
- [ ] Database table: `voided_receipts` (id, invoice_id, void_reason_code, void_notes, voided_by, voided_at, approved_by)
- [ ] Cron job: Daily gap detection script (runs at midnight, checks previous day)
- [ ] API endpoint: `/api/receipts/sequence-control.php` (actions: detect_gaps, void_receipt, resolve_gap)
- [ ] UI component: Receipt void button with reason dropdown + notes textarea (required fields)
- [ ] UI page: Gap resolution interface for supervisors (list gaps, view details, approve/reject)
- [ ] Stored procedure: `sp_detect_receipt_gaps` (per sales point, date range)
- [ ] Notification service: Email/SMS alert for detected gaps with gap details
- [ ] Unit tests: Gap detection algorithm, void validation, supervisor approval workflow
- [ ] Integration tests: End-to-end void workflow, gap detection and resolution

**Planning Trigger:**
When user requests planning for:
- "POS system", "Point of Sale", "sales entry", "checkout system", "cashier interface"
- "Invoice recording", "receipt management", "sales transaction capture"

**Automatically include M1 and M2** in the specification and implementation plan.

**Compliance Note:**
These controls address **Recommendation #2** (Real-Time Transaction Capture) and **Recommendation #6** (Sequential Receipt Control) from the Finance Revenue Management audit findings. Non-implementation creates **high-risk audit exposure** and **potential regulatory non-compliance**.

---

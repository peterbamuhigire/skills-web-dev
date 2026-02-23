# Software User Manual (SUM) Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [manual-guide](../../manual-guide/SKILL.md) (ERP-specific in-app manuals) | [report-print-pdf](../../report-print-pdf/SKILL.md) (PDF/print patterns)

## Purpose

Guide end-users on how to install, configure, use, and troubleshoot the software. This is the primary document users reference when learning and using the system.

**Audience:** Franchise owners, staff, members (non-technical users)

**Relationship to `manual-guide` skill:** This template provides the SDLC-standard document structure for a complete Software User Manual. The `manual-guide` skill provides the interactive, web-based (PHP) manual system delivered inside the application. Use both together -- this template for the formal document, `manual-guide` for the in-app experience.

---

## Template

### 1. Document Information

```markdown
# {Product Name} — Software User Manual

| Field | Value |
|-------|-------|
| Document Version | {1.0} |
| Date | {YYYY-MM-DD} |
| Product Version | {1.0.0} |
| Target Audience | {Franchise owners, staff, members} |
| Classification | {Internal / Public} |
| Prepared By | {Author name / team} |
| Approved By | {Product owner / stakeholder} |
```

### 2. About This Manual

**Guidance:** Set expectations for what this manual covers, who it is for, and how to navigate it.

```markdown
## About This Manual

### Purpose and Scope
This manual covers all features of {Product Name} version {X.X} for
{web application / Android app / both}. It guides you through daily tasks
from logging in to generating reports.

### How to Use This Manual
- **New users:** Start with "Getting Started" and follow sequentially
- **Experienced users:** Use the Table of Contents to jump to specific features
- **Troubleshooting:** Skip to the Troubleshooting section at the end

### Conventions Used
| Convention | Meaning |
|-----------|---------|
| **Bold text** | UI element (button, menu, field name) |
| `Monospace` | Text you type or values you see |
| > Note | Important information |
| > Warning | Risk of data loss or error |

### Where to Get Help
- **In-app help:** Click the **?** icon on any page
- **Support email:** {support@example.com}
- **Phone:** {+256-XXX-XXXXXX} (Mon-Fri, 8AM-5PM EAT)
```

### 3. Getting Started

**Guidance:** Cover everything a first-time user needs to get productive.

#### 3.1 System Requirements

```markdown
## System Requirements

### Web Application
| Requirement | Minimum |
|------------|---------|
| Browser | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+ |
| Screen Resolution | 1024x768 (1366x768 recommended) |
| Internet | Stable broadband connection |
| JavaScript | Enabled |

### Android Application
| Requirement | Minimum |
|------------|---------|
| Android Version | Android 10 (API 29) or higher |
| RAM | 2 GB minimum |
| Storage | 100 MB free space |
| Internet | Required for sync; offline mode available for core features |
```

#### 3.2 Account Setup and First Login

```markdown
## Account Setup and First Login

### Receiving Your Credentials
Your system administrator will provide:
- **Login URL:** https://{your-domain.com}/sign-in.php
- **Email or Username**
- **Temporary Password**

### First-Time Login
1. Open your browser and navigate to the **Login URL**
2. Enter your **Email** and **Temporary Password**
3. Click **Sign In**
4. You will be prompted to **change your password**
   - Minimum 8 characters, include uppercase, lowercase, and a number
5. After changing your password, you will see the **Dashboard**

[Screenshot: First login screen with email and password fields -- sign-in.png]

### Biometric Setup (Android)
1. Open the app and log in with your credentials
2. Go to **Settings** > **Security**
3. Toggle **Biometric Login** to ON
4. Confirm with your fingerprint or face scan
5. Next launch will offer biometric authentication
```

#### 3.3 Dashboard Overview

```markdown
## Dashboard Overview

[Screenshot: Main dashboard with KPI cards and navigation -- dashboard.png]

### Layout
| Area | Description |
|------|-------------|
| **Top Navigation Bar** | Logo, search, notifications, profile menu |
| **Side Menu** | Module navigation (visible on desktop, hamburger on mobile) |
| **KPI Cards** | Key performance indicators (today's sales, pending orders, etc.) |
| **Quick Actions** | Frequently used shortcuts (New Sale, New Customer, etc.) |
| **Recent Activity** | Latest system events and updates |

### Navigation Guide
- **Breadcrumbs:** Show your location (Home > Sales > Invoices)
- **Side Menu:** Click any module name to expand sub-items
- **Search:** Press Ctrl+K (or Cmd+K on Mac) to search anywhere
```

#### 3.4 Role-Based Access

```markdown
## Role-Based Access

Your role determines what you can see and do:

| Role | Access Level | Typical User |
|------|-------------|--------------|
| Super Admin | Full system access, all tenants | Platform operator |
| Franchise Owner | Full franchise access, reports, settings | Business owner |
| Staff | Task-specific access based on permissions | Employee |
| Member | Self-service portal only | End customer |

> **Note:** If you need access to a feature you cannot see, contact your
> Franchise Owner or system administrator.
```

### 4. Feature Guides (Per Module)

**Guidance:** Create one section per module. Use this structure for each.

```markdown
## {Module Name} (e.g., Sales Management)

### Overview
{1-2 sentences: what this module does and who uses it}

### {Workflow Name} (e.g., Create a New Invoice)

**Prerequisites:** {What must exist first, e.g., at least one customer}

**Steps:**
1. Navigate to **Sales** > **Invoices**
2. Click the **+ New Invoice** button
3. Select the **Customer** from the dropdown
   - If the customer does not exist, click **+ Add Customer**
4. Add line items:
   a. Click **Add Item**
   b. Search for the product by name or code
   c. Enter the **Quantity**
   d. The **Price** auto-fills from the product catalog
5. Review the **Subtotal**, **Tax**, and **Total**
6. Click **Save as Draft** or **Finalize Invoice**
7. To print or export, click **Print** or **Download PDF**

**Expected Result:** Invoice appears in the invoice list with status "Draft" or "Finalized."

[Screenshot: Invoice creation form with line items -- create-invoice.png]

**Common Mistakes and Fixes:**
| Mistake | Fix |
|---------|-----|
| Wrong customer selected | Click **Edit** on the invoice, change customer before finalizing |
| Price shows 0.00 | Product has no price set; update in **Products** > **Edit** |
| Cannot finalize | Missing required fields; check for red-highlighted fields |

### Data Entry Best Practices
- Enter dates in YYYY-MM-DD format
- Use the search/filter before creating duplicates
- Save drafts frequently for large entries

### Filtering, Searching, and Sorting
- **Search bar:** Type any keyword to filter the table
- **Column headers:** Click to sort ascending/descending
- **Date range:** Use the date picker to filter by period
- **Export:** Click **Export** to download filtered data as CSV or PDF
```

### 5. Mobile App Guide (Android)

```markdown
## Mobile App Guide (Android)

### Installation
1. Open the **Google Play Store** on your Android device
2. Search for **{Product Name}**
3. Tap **Install**
4. Once installed, tap **Open**

### Login and Offline Mode
- Log in with the same credentials as the web application
- **Offline mode:** Core features (view data, draft entries) work without internet
- **Sync indicator:** A green dot means synced; orange means pending sync
- Data syncs automatically when connectivity is restored

### Key Differences from Web Version
| Feature | Web | Android |
|---------|-----|---------|
| Data entry | Full keyboard, large screen | Optimized forms, camera input |
| Reports | Full report suite | Summary reports only |
| Settings | Full configuration | View-only (configure on web) |
| Offline | Not available | Core features available |

### Push Notifications
1. Go to **Settings** > **Notifications**
2. Enable the notification types you want (orders, alerts, reminders)
3. Notifications appear in the system tray and the in-app **Bell** icon

### Data Sync Behavior
- **Automatic sync:** Every 15 minutes when connected
- **Manual sync:** Pull down on any list screen to refresh
- **Conflict resolution:** Server version wins; your local draft is saved as "conflicted"
- **Offline edits:** Queued and sent in order when connectivity returns
```

### 6. Troubleshooting

```markdown
## Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Cannot log in | Wrong password or account locked | Use "Forgot Password" or contact admin |
| Page loads slowly | Poor internet or heavy data | Refresh, check connection, reduce date range |
| Data not showing | Wrong date filter or franchise | Check filters, verify you are in the correct franchise |
| PDF export fails | Browser popup blocker | Allow popups for this site |
| Mobile app crashes on launch | Outdated app version | Update from Play Store |
| "Session expired" message | Inactivity timeout (30 min) | Log in again; unsaved work may be lost |

### Error Messages Guide
| Error | Meaning | Action |
|-------|---------|--------|
| "Access Denied" | You lack permission for this action | Contact your admin to request access |
| "Record Not Found" | Data was deleted or you lack access | Verify the record exists; check franchise scope |
| "Validation Error" | Required field missing or invalid format | Check highlighted fields, correct input |
| "Server Error (500)" | Backend issue | Wait 1 minute and retry; report if persistent |

### How to Report a Bug
Include the following when reporting:
1. **What you were doing** (step-by-step)
2. **What you expected to happen**
3. **What actually happened** (including error messages)
4. **Screenshot** of the error
5. **Browser/device** information
6. **Date and time** of the issue
```

### 7. FAQ

```markdown
## Frequently Asked Questions

**Q: Can I use the system on my phone's browser?**
A: The web app is responsive but we recommend the Android app for mobile use.

**Q: How do I reset my password?**
A: Click "Forgot Password" on the login page, or ask your admin to reset it.

**Q: Can I access data from another franchise?**
A: No. Each franchise's data is strictly isolated for security.

**Q: How often is data backed up?**
A: Daily automated backups. Contact your admin for restore requests.

**Q: Can I export data to Excel?**
A: Yes. Most list views have an **Export** button for CSV and PDF formats.
```

### 8. Glossary and Appendices

```markdown
## Glossary
| Term | Definition |
|------|-----------|
| Franchise | A tenant/business unit in the system |
| Dashboard | The main overview screen after login |
| KPI | Key Performance Indicator -- a summary metric |
| RBAC | Role-Based Access Control -- permissions by role |
| Sync | Synchronizing local mobile data with the server |

## Appendix A: Keyboard Shortcuts (Web)
| Shortcut | Action |
|----------|--------|
| Ctrl+K / Cmd+K | Global search |
| Ctrl+S / Cmd+S | Save current form |
| Esc | Close modal/dialog |

## Appendix B: Supported File Formats for Uploads
| Type | Formats | Max Size |
|------|---------|----------|
| Images | JPG, PNG, WebP | 2 MB (auto-compressed) |
| Documents | PDF, DOCX, XLSX | 10 MB |
| Imports | CSV | 5 MB |

## Feedback and Support
We value your feedback. Contact us at {support@example.com} or use the
in-app **Feedback** button to report issues or suggest improvements.
```

---

## Screenshot Placeholder Format

Use this consistent format throughout the manual:

```
[Screenshot: {Brief description of what the screenshot shows} -- {filename}.png]
```

**Examples:**
- `[Screenshot: Login page with email and password fields -- sign-in.png]`
- `[Screenshot: Dashboard KPI cards showing today's revenue -- dashboard-kpis.png]`
- `[Screenshot: Invoice creation form with 3 line items -- create-invoice.png]`

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Technical jargon without definition | End-users do not understand "JWT", "CORS", "API" | Use plain language; add glossary for necessary terms |
| Assuming user knowledge | "Configure your environment" means nothing to a cashier | Spell out every step with no assumptions |
| No screenshots or visual aids | Users cannot identify the right buttons and fields | Add screenshot placeholders for every workflow |
| No troubleshooting section | Users get stuck with no path to resolution | Include common issues table with solutions |
| Giant wall of text | Users skip it entirely | Use tables, numbered steps, and short paragraphs |
| Documenting the UI structure instead of tasks | Users want "How do I create an invoice?" not "The Invoices page has these buttons" | Organize by user goals, not by screen layout |

## Quality Checklist

- [ ] Every module in the SRS has a corresponding Feature Guide section
- [ ] All workflows have numbered steps with expected results
- [ ] Screenshot placeholders use consistent format
- [ ] Troubleshooting covers at least 10 common issues
- [ ] FAQ covers at least 10 questions
- [ ] Glossary defines all technical terms used
- [ ] Mobile app section covers installation, offline, and sync
- [ ] Role-based access table matches RBAC configuration
- [ ] No technical jargon without plain-language explanation
- [ ] Document stays under 500 lines (split into sub-files if needed)
- [ ] Active voice and present tense throughout
- [ ] Consistent bold formatting for all UI element references

---

**Back to:** [SKILL.md](../SKILL.md)

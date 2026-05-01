# Training Materials Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [software-user-manual.md](software-user-manual.md) (reference material for training) | [manual-guide](../../manual-guide/SKILL.md) (in-app help system)

## Purpose

Help users learn the software quickly and effectively through structured training programs, tutorials, hands-on exercises, and assessments. Training materials complement the Software User Manual -- the manual is the reference; training materials are the learning experience.

**Audience:** New users, trainers, HR/onboarding teams

---

## Template

### 1. Document Information

```markdown
# {Product Name} — Training Materials

| Field | Value |
|-------|-------|
| Document Version | {1.0} |
| Date | {YYYY-MM-DD} |
| Product Version | {1.0.0} |
| Prepared By | {Training coordinator / Author} |
```

### 2. Training Program Overview

```markdown
## Training Program Overview

### Training Objectives
By the end of this training program, participants will be able to:
1. Log in and navigate the system confidently
2. Perform their role-specific daily tasks without assistance
3. Generate and interpret reports relevant to their role
4. Troubleshoot common issues independently
5. Know when and how to escalate technical problems

### Target Audience Segments
| Segment | Role | Training Duration | Delivery Method |
|---------|------|-------------------|-----------------|
| Super Admin | Platform operator | 2 days (16 hours) | Instructor-led + hands-on |
| Franchise Owner | Business owner | 1 day (8 hours) | Instructor-led + hands-on |
| Staff | Daily operator | 4 hours | Self-paced + instructor Q&A |
| Member / Customer | End user | 30 minutes | Self-paced (video + guide) |

### Training Delivery Methods
| Method | Best For | Tools |
|--------|----------|-------|
| Instructor-led | Complex workflows, admin training | Screen share, sandbox environment |
| Self-paced | Staff onboarding, member portal | Written guides, video tutorials |
| Video tutorials | Visual learners, mobile users | 2-5 minute focused recordings |
| Hands-on labs | Skill verification, practical mastery | Sandbox tenant with test data |

### Training Schedule Template
| Day | Session | Duration | Audience | Topics |
|-----|---------|----------|----------|--------|
| Day 1 AM | System Overview | 2 hours | All | Login, dashboard, navigation |
| Day 1 PM | Core Features | 3 hours | All | Data entry, search, reports |
| Day 2 AM | Role-Specific | 3 hours | Per role | Admin: settings, users. Staff: daily tasks |
| Day 2 PM | Practice + Assessment | 2 hours | All | Hands-on labs, knowledge check |
```

### 3. Quick Start Guides

**Guidance:** 5-minute guides that get each role to their first meaningful action.

```markdown
## Quick Start Guides

### Quick Start: Franchise Owner (5 minutes)
1. **Log in** at https://{domain}/sign-in.php with your credentials
2. **Change your password** when prompted (min 8 chars, mixed case + number)
3. **View your Dashboard** -- note the KPI cards showing today's metrics
4. **Check your team:** Go to **Settings** > **Users** to see staff accounts
5. **View a report:** Go to **Reports** > **Daily Summary** and click **Generate**

> You are now oriented. Continue with Tutorial Module 1 for detailed training.

### Quick Start: Staff Member (5 minutes)
1. **Log in** with the credentials your manager provided
2. **Review your Dashboard** -- your assigned tasks appear at the top
3. **Complete your first task:** Click a pending task and follow the on-screen steps
4. **Save your work:** Click **Save** (drafts auto-save every 60 seconds)
5. **Log out:** Click your name (top right) > **Sign Out** when done

### Quick Start: Super Admin (5 minutes)
1. **Log in** at https://{domain}/adminpanel/sign-in.php
2. **View system overview:** Dashboard shows all tenants, active users, system health
3. **Check tenants:** Go to **Franchises** to see all registered tenants
4. **Review system settings:** Go to **Settings** for global configuration
5. **Check audit log:** Go to **Security** > **Audit Trail** for recent activity

### Quick Start: Member / Customer (3 minutes)
1. **Log in** at https://{domain}/memberpanel/sign-in.php
2. **View your profile:** Click your name to see/edit personal information
3. **Check your history:** Navigate to **My {Orders/Records/Transactions}**
4. **Update preferences:** Go to **Settings** to manage notifications
```

### 4. Tutorial Modules

**Guidance:** Each tutorial follows a consistent structure. Create one per major feature.

```markdown
## Tutorial Modules

### Tutorial Structure (Standard Format)

Every tutorial follows this format:

---
**Tutorial {Number}: {Title}**
**Learning Objective:** After this tutorial, you will be able to {specific action}.
**Time Estimate:** {5-15} minutes
**Prerequisites:** {Complete Tutorial X first / None}
**Role:** {Which roles this applies to}

**Walkthrough:**
1. {Step 1 with specific instructions}
   [Screenshot: {description} -- {filename}.png]
2. {Step 2}
3. {Step 3}

**Practice Exercise:**
- {Hands-on task the learner should perform}
- **Acceptance Criteria:** {How to verify they did it correctly}

**Knowledge Check:**
1. {Question about the workflow} → Answer: {answer}
2. {Question about common mistakes} → Answer: {answer}
---

### Tutorial Sequence by Role

**Franchise Owner Path:**
| Order | Tutorial | Topic | Time |
|-------|----------|-------|------|
| 1 | System Navigation | Dashboard, menus, search | 10 min |
| 2 | User Management | Add staff, assign roles, permissions | 15 min |
| 3 | Core Module Overview | {Primary module walkthrough} | 15 min |
| 4 | Reports and Analytics | Generate, filter, export reports | 10 min |
| 5 | Settings and Configuration | Business settings, preferences | 10 min |

**Staff Path:**
| Order | Tutorial | Topic | Time |
|-------|----------|-------|------|
| 1 | System Navigation | Dashboard, menus, search | 10 min |
| 2 | Data Entry Basics | Create, edit, search records | 15 min |
| 3 | Daily Workflow | {Role-specific daily tasks} | 15 min |
| 4 | Reports | View and export relevant reports | 10 min |

### Example Tutorial

**Tutorial 1: Creating Your First {Record Type}**
**Learning Objective:** Create and save a complete {record} with all required fields.
**Time Estimate:** 10 minutes
**Prerequisites:** Completed login and navigation tutorial
**Role:** Franchise Owner, Staff

**Walkthrough:**
1. Navigate to **{Module}** > **{Sub-section}** in the side menu
   [Screenshot: Side menu with {Module} highlighted -- nav-module.png]
2. Click the **+ New {Record}** button (top right)
3. Fill in required fields:
   - **{Field 1}:** {Description of what to enter}
   - **{Field 2}:** {Description, note any formatting rules}
   - **{Field 3}:** Select from dropdown
4. Click **Save**
5. Verify: The new record appears in the list with status "Active"
   [Screenshot: List view with new record visible -- record-created.png]

**Practice Exercise:**
Create 3 test {records} with different values. Verify each appears in the list.
**Acceptance Criteria:** All 3 records visible in the list with correct status.

**Knowledge Check:**
1. What happens if you leave a required field empty? → Answer: A red validation message appears and the record is not saved.
2. Where do you find a record you just created? → Answer: In the {Module} list view, sorted by most recent.
```

### 5. Video Script Templates

```markdown
## Video Script Templates

### Video Format Standard
- **Length:** 2-5 minutes (never exceed 5 minutes)
- **Resolution:** 1920x1080
- **Audio:** Clear voiceover, no background music during instructions
- **Captions:** Required (for accessibility and non-English speakers)

### Script Template
TITLE: {Feature Name} — How to {Action}
DURATION: {X} minutes
AUDIENCE: {Role}

[INTRO — 15 seconds]
Voiceover: "In this video, you will learn how to {action} in {Product Name}."
Screen: Show the starting point (e.g., Dashboard)

[CONTEXT — 20 seconds]
Voiceover: "You would use this when {use case scenario}."
Screen: Brief view of the workflow context

[DEMO — 2-4 minutes]
Voiceover: Step-by-step narration matching on-screen actions
Screen: Full screen recording with cursor highlights
- Step 1: "{Narrate action}" [click/type shown on screen]
- Step 2: "{Narrate action}"
- Step 3: "{Narrate action}"

[RECAP — 15 seconds]
Voiceover: "To recap: you {step 1}, then {step 2}, and finally {step 3}."
Screen: Show the end result

[CALL TO ACTION — 10 seconds]
Voiceover: "Now try this yourself in the practice environment.
For more tutorials, visit the Training section."

### Screen Recording Guidelines
- Use a clean browser profile (no personal bookmarks)
- Use test data that looks realistic but is obviously fake
- Highlight clicks with a visible cursor effect
- Zoom into small UI elements
- Pause briefly on important screens (1-2 seconds)
```

### 6. Hands-On Lab Exercises

```markdown
## Hands-On Lab Exercises

### Lab Environment Setup
- Create a dedicated **training tenant** (franchise) with pre-loaded test data
- Test data should include: 5 customers, 10 products, 3 staff users, sample transactions
- Reset training tenant data before each training session
- Provide each trainee with unique credentials (trainee01@example.com through trainee20@example.com)

### Lab Exercise Template

**Lab {Number}: {Title}**
**Scenario:** {Real-world scenario the trainee must solve}
**Time Limit:** {15-30 minutes}
**Difficulty:** {Beginner / Intermediate / Advanced}

**Tasks:**
1. [ ] {Task description with acceptance criteria}
2. [ ] {Task description with acceptance criteria}
3. [ ] {Task description with acceptance criteria}

**Hints (Progressive Disclosure):**
- Hint 1: {Gentle nudge — which menu to look in}
- Hint 2: {More specific — which button to click}
- Hint 3: {Near-solution — step-by-step abbreviated}

**Solution Walkthrough:**
{Step-by-step solution — shown only after trainee attempts}

**Assessment Rubric:**
| Criteria | Points | Achieved? |
|----------|--------|-----------|
| All tasks completed correctly | 50 | [ ] |
| Completed within time limit | 20 | [ ] |
| No errors or corrections needed | 20 | [ ] |
| Used efficient workflow (not trial-and-error) | 10 | [ ] |
```

### 7. Mobile App Training

```markdown
## Mobile App Training

### Android App Installation Walkthrough
1. Open **Google Play Store** on your Android device
2. Search for **{Product Name}**
3. Tap **Install** (requires Android 10+)
4. Open the app after installation
5. Log in with your web credentials

### Offline Mode Training
**Objective:** Understand what works offline and what requires internet.

| Feature | Online | Offline |
|---------|--------|---------|
| View records | Yes | Yes (cached) |
| Create new records | Yes | Yes (queued) |
| Generate reports | Yes | No |
| Sync data | Automatic | Manual (pull down) |

**Exercise:** Turn on airplane mode. Create a record. Turn off airplane mode. Verify the record syncs.

### Mobile-Specific Features
- **Camera input:** Tap the camera icon to capture documents
- **Barcode scanning:** Point camera at barcode to auto-fill product
- **Push notifications:** Configure in Settings > Notifications
- **Biometric login:** Enable in Settings > Security
```

### 8. Training Assessment

```markdown
## Training Assessment

### Pre-Training Survey (5 minutes)
1. How familiar are you with {Product Name}? (1-5 scale)
2. What is your primary role? (dropdown)
3. Which features do you expect to use most? (checkboxes)
4. Have you used similar software before? (Yes/No)
5. What concerns do you have about the new system? (open text)

### Post-Training Quiz (10 minutes, 20 questions)
Format: Multiple choice (4 options, 1 correct)

Sample questions:
1. Where do you find the daily sales report?
   a) Settings > Reports  b) Dashboard > KPI cards
   c) **Reports > Daily Summary**  d) Sales > History

2. What happens when you save a record offline?
   a) It is lost  b) **It queues and syncs when online**
   c) An error appears  d) It saves to your phone only

**Pass threshold:** 80% (16/20 correct)

### Practical Assessment (30 minutes)
Trainee must complete 5 tasks independently:
1. Log in and navigate to the {primary module}
2. Create a complete {record} with all required fields
3. Search for an existing record and edit one field
4. Generate a report for a specific date range and export as PDF
5. Add a new staff user with specific permissions (Owner role only)

**Pass criteria:** All 5 tasks completed correctly without assistance.
```

### 9. Train-the-Trainer Guide

```markdown
## Train-the-Trainer Guide

### Preparation Checklist
- [ ] Complete all training modules yourself first
- [ ] Set up training tenant with fresh test data
- [ ] Prepare trainee credentials (1 per participant)
- [ ] Test projector/screen share and internet connectivity
- [ ] Print quick reference cards (1 per participant)
- [ ] Prepare feedback forms

### Common Questions and Answers
| Question | Answer |
|----------|--------|
| "Can I access this from home?" | Yes, it is web-based. Use any supported browser. |
| "What if I make a mistake?" | Most actions can be edited or reversed. Deleted records can be restored by admin. |
| "Is my data safe?" | Yes. Data is encrypted, backed up daily, and isolated per franchise. |
| "Will I lose my data if the internet goes down?" | Web: save often. Mobile: offline mode preserves your work. |

### Training Material Maintenance
- **Update schedule:** Review and update with each product release
- **Version tracking:** Match training version to product version
- **Feedback incorporation:** Review trainee feedback monthly; update materials quarterly
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Training = reading the manual | Adults learn by doing, not reading | Include hands-on labs for every module |
| No time estimates | Trainees and trainers cannot plan | Add realistic time estimates per section |
| One-size-fits-all training | Admin and cashier have different needs | Create role-specific learning paths |
| No assessment | Cannot verify learning happened | Include quiz + practical assessment |
| Outdated training materials | Trainees learn the wrong UI/workflow | Update materials with every release |
| 30-minute+ videos | Attention drops after 5 minutes | Keep videos under 5 minutes; break into series |
| No practice environment | Trainees afraid to "break something" | Set up a sandbox tenant with test data |
| Training only at onboarding | Users forget over time | Provide refresher materials and reference cards |

## Quality Checklist

- [ ] Training paths defined for each role (Super Admin, Owner, Staff, Member)
- [ ] Quick start guides exist for each role (under 5 minutes each)
- [ ] At least 5 tutorial modules with consistent structure
- [ ] Video script templates follow the 2-5 minute standard
- [ ] Hands-on lab exercises have progressive hints and solutions
- [ ] Mobile app training covers installation, offline mode, and sync
- [ ] Pre-training survey and post-training quiz prepared
- [ ] Practical assessment with clear pass criteria defined
- [ ] Train-the-trainer guide with preparation checklist and FAQ
- [ ] Training materials versioned to match product version
- [ ] All screenshot placeholders use consistent format
- [ ] Document stays under 500 lines (split into sub-files if needed)

---

**Back to:** [SKILL.md](../SKILL.md)

# Common Workflows

This guide covers common workflows when working with the skills repository.

## Workflow 1: User Requests Skill Usage

**Scenario:** User asks for help that aligns with an existing skill.

**Example:**
```
User: "I need help with multi-tenant authentication"
```

**Claude's Steps:**

1. **Recognize skill alignment**
   - Identify: "This aligns with multi-tenant-saas-architecture skill"

2. **Reference or load the skill**
   - Load the skill content
   - Parse frontmatter and body

3. **Apply patterns from skill**
   - Follow authentication patterns
   - Use tenant isolation strategies
   - Apply security best practices

4. **Provide implementation guidance**
   - Generate code per skill's patterns
   - Reference examples from skill
   - Follow best practices exactly

**Output Example:**

```
I'll use the multi-tenant-saas-architecture skill to implement secure
multi-tenant authentication.

[Provides implementation following skill patterns]
```

## Workflow 2: User Asks to Add Skill

**Scenario:** User wants to create a new skill.

**Example:**
```
User: "Create a skill for API design patterns"
```

**Claude's Steps:**

1. **Review existing skills for format**
   - Read 2-3 existing skills
   - Understand structure and frontmatter
   - Note common patterns

2. **Create skill directory**
   ```bash
   mkdir skills/api-design-patterns
   ```

3. **Write SKILL.md with comprehensive patterns**
   ```yaml
   ---
   name: api-design-patterns
   description: "Use when designing REST APIs, defining endpoints, or standardizing API conventions"
   ---

   # API Design Patterns

   [Comprehensive patterns, examples, best practices]
   ```

4. **Update README.md with new skill entry**
   ```markdown
   ### API Design

   - **api-design-patterns:** REST API design, endpoints, conventions
   ```

5. **Update PROJECT_BRIEF.md**
   ```markdown
   ## Skills

   - **api-design-patterns:** API design patterns and standards
   ```

6. **Commit with clear message**
   ```bash
   git add skills/api-design-patterns/ README.md PROJECT_BRIEF.md
   git commit -m "feat: add api-design-patterns skill for REST API design"
   ```

## Workflow 3: Cross-Project Usage

**Scenario:** User in a different project wants to use a skill.

**Example:**
```
User in Project A: "Use the webapp-gui-design skill"
```

**Claude's Steps:**

1. **Confirm skill location**
   - Check: "Is the skills/ directory present in this project?"
   - If yes: It's a local copy or git submodule
   - If no: Ask user to set it up

2. **Load skill content**
   - Read skills/webapp-gui-design/SKILL.md
   - Parse frontmatter and patterns

3. **Apply to Project A's context**
   - Understand Project A's tech stack
   - Adapt patterns to fit
   - Maintain skill's core principles

4. **Generate code following skill patterns**
   - Use established templates
   - Apply optional bespoke aesthetics
   - Follow UI best practices from skill

## Workflow 4: Modifying Existing Skill

**Scenario:** User wants to improve an existing skill.

**Example:**
```
User: "Update the mysql-best-practices skill with indexing strategies"
```

**Claude's Steps:**

1. **Read current skill**
   ```bash
   cat skills/mysql-best-practices/SKILL.md
   ```

2. **Identify insertion point**
   - Find relevant section (e.g., "Performance Optimization")
   - Or create new section if needed

3. **Make targeted improvements**
   - Add indexing strategies section
   - Include examples
   - Add anti-patterns

4. **Maintain structure**
   - Keep frontmatter intact
   - Don't rewrite entire skill
   - Stay under 500 lines

5. **Update docs if needed**
   - If significant: Update README.md description
   - If examples changed: Update references

6. **Commit**
   ```bash
   git add skills/mysql-best-practices/
   git commit -m "improve: add indexing strategies to mysql-best-practices"
   ```

## Workflow 5: Creating Multi-File Skill

**Scenario:** Skill needs more than 500 lines of content.

**Example:**
```
User: "Create a comprehensive CI/CD skill"
```

**Claude's Steps:**

1. **Plan structure**
   ```
   skills/ci-cd-automation/
   ├── SKILL.md                  # Core patterns (500 lines max)
   ├── references/
   │   ├── github-actions.md     # GitHub Actions guide
   │   ├── gitlab-ci.md          # GitLab CI guide
   │   └── jenkins.md            # Jenkins guide
   ├── documentation/
   │   ├── docker-deployment.md  # Docker deployment
   │   └── monitoring.md         # Monitoring setup
   └── examples/
       ├── .github/workflows/
       └── .gitlab-ci.yml
   ```

2. **Write SKILL.md (core patterns only)**
   - Overview of CI/CD principles
   - Common patterns (75-90% use cases)
   - Quick reference table
   - Links to references/ for deep dives

3. **Create supporting documents**
   - Each reference doc: Max 500 lines
   - Focused on specific CI/CD platform
   - Complete examples

4. **Reference supporting files in SKILL.md**
   ```markdown
   ## Platform-Specific Guides

   - GitHub Actions: See `references/github-actions.md`
   - GitLab CI: See `references/gitlab-ci.md`
   - Jenkins: See `references/jenkins.md`
   ```

5. **Commit all files**
   ```bash
   git add skills/ci-cd-automation/
   git commit -m "feat: add ci-cd-automation skill with platform-specific guides"
   ```

## Workflow 6: Combining Multiple Skills

**Scenario:** Task requires multiple skill domains.

**Example:**
```
User: "Using webapp-gui-design and multi-tenant-saas-architecture, create a multi-tenant dashboard"
```

**Claude's Steps:**

1. **Load both skills**
   - Read webapp-gui-design/SKILL.md
   - Read multi-tenant-saas-architecture/SKILL.md

2. **Identify integration points**
   - UI layer: webapp-gui-design patterns
   - Backend layer: multi-tenant-saas-architecture patterns
   - Both: Security considerations

3. **Apply each skill to its domain**
   - UI components: Follow webapp-gui-design
   - Tenant isolation: Follow multi-tenant-saas-architecture
   - Database queries: Include tenant_id filters

4. **Ensure consistency**
   - UI calls backend with tenant context
   - Backend enforces tenant isolation
   - Security applied at all layers

## Workflow 7: Skill Safety Audit

**Scenario:** User adds new skills and wants to verify security.

**Example:**
```
User: "Run skill-safety-audit on new skills"
```

**Claude's Steps:**

1. **Identify new/modified skills**
   ```bash
   git diff --name-only HEAD~1 HEAD | grep SKILL.md
   ```

2. **For each skill, check:**
   - [ ] No hardcoded credentials
   - [ ] No SQL injection patterns
   - [ ] No XSS vulnerabilities in examples
   - [ ] No insecure file operations
   - [ ] No dangerous command execution
   - [ ] Proper error handling
   - [ ] Security best practices followed

3. **Generate audit report**
   ```markdown
   # Skill Safety Audit - 2026-02-07

   ## Skills Audited
   - api-design-patterns
   - new-skill-name

   ## Findings
   - ✅ api-design-patterns: No issues
   - ⚠️ new-skill-name: Example uses string concatenation for SQL (line 145)

   ## Recommendations
   - Update new-skill-name line 145 to use prepared statements
   ```

4. **Fix issues if found**

## Workflow 8: Documentation Cleanup

**Scenario:** After major changes, clean up documentation.

**Example:**
```
User: "Run markdown-lint-cleanup on skills docs"
```

**Claude's Steps:**

1. **Check all .md files for line count**
   ```bash
   find skills/ -name "*.md" -exec wc -l {} + | sort -rn
   ```

2. **Identify files over 500 lines**
   - Flag for refactoring
   - Plan split strategy

3. **Check markdown formatting**
   - Proper heading hierarchy
   - Code blocks have language specified
   - Tables are well-formatted
   - Links are valid

4. **Verify TOC structure**
   - Tier 1 docs link to Tier 2
   - All referenced docs exist
   - No broken links

5. **Update as needed**
   - Fix formatting issues
   - Split oversized files
   - Update cross-references

## Workflow 9: Skill Deprecation

**Scenario:** A skill is replaced by a better approach.

**Example:**
```
User: "Deprecate old-api-patterns skill in favor of new api-design-patterns"
```

**Claude's Steps:**

1. **Don't delete the old skill**
   - Keep for historical reference
   - Existing projects may depend on it

2. **Add deprecation notice**
   ```markdown
   ---
   name: old-api-patterns
   description: "DEPRECATED - Use api-design-patterns instead"
   status: deprecated
   ---

   # Old API Patterns (DEPRECATED)

   **⚠️ This skill is deprecated. Please use `api-design-patterns` instead.**

   **Reason:** api-design-patterns provides more comprehensive coverage
   and updated best practices.

   **Migration Guide:** See `api-design-patterns/SKILL.md`

   ---

   [Original content remains for reference]
   ```

3. **Update README.md**
   ```markdown
   ### API Design

   - **api-design-patterns:** REST API design, endpoints, conventions
   - ~~**old-api-patterns:**~~ DEPRECATED - Use api-design-patterns
   ```

4. **Document migration path**
   - Create migration guide
   - Note key differences
   - Provide examples

## Workflow 10: Skill Review Cycle

**Scenario:** Regular maintenance and review.

**Example:**
```
User: "Review all skills for outdated patterns"
```

**Claude's Steps:**

1. **List all skills**
   ```bash
   ls -1 skills/*/SKILL.md
   ```

2. **For each skill, check:**
   - Technology versions current?
   - Examples still work?
   - Best practices up to date?
   - Links valid?
   - Under 500 lines?

3. **Create improvement checklist**
   ```markdown
   # Skill Review - 2026-02-07

   - [ ] webapp-gui-design: Update Bootstrap 5.3 examples
   - [ ] mysql-best-practices: Add MySQL 9.x features
   - [x] multi-tenant-saas-architecture: Current
   - [ ] report-print-pdf: Update mPDF to latest version
   ```

4. **Schedule updates**
   - High priority: Security-related
   - Medium: Technology updates
   - Low: Documentation improvements

## Workflow 11: Project-Specific Skill Setup

**Scenario:** Setting up skills for a new project.

**Example:**
```
User: "Set up skills repository for new project"
```

**Claude's Steps:**

1. **Add skills as git submodule**
   ```bash
   cd /path/to/new-project
   git submodule add <skills-repo-url> skills
   ```

2. **Document in project CLAUDE.md**
   ```markdown
   ## AI Skills Usage (Required)

   Before planning or implementing work, proactively explore and apply
   relevant skills from the `skills/` directory.

   - Start with `skills/README.md` to identify applicable skills
   - Follow `skills/<skill-name>/SKILL.md` for task-specific patterns

   ## Available Skills

   - **multi-tenant-saas-architecture:** Use for tenant isolation features
   - **mysql-best-practices:** MANDATORY for all database work
   - **webapp-gui-design:** Use for UI development
   ```

3. **Create project-specific guidance**
   ```markdown
   ## When to Use Which Skill

   ### Database Work
   Always use: `mysql-best-practices`

   ### UI Development
   Always use: `webapp-gui-design` + `vibe-security-skill`

   ### New Features
   Start with: `feature-planning`
   Then use: Relevant implementation skills
   ```

## Workflow 12: Testing Skill Changes

**Scenario:** Verify skill improvements work as intended.

**Example:**
```
User: "Test the updated mysql-best-practices skill"
```

**Claude's Steps:**

1. **Create test scenario**
   - Design a database migration task
   - Use patterns from updated skill

2. **Apply skill to test scenario**
   - Load the skill
   - Follow patterns exactly
   - Generate migration code

3. **Verify output**
   - Migration follows checklist?
   - Uses proper naming conventions?
   - Includes rollback plan?
   - Has error handling?

4. **Test in safe environment**
   - Run migration on test database
   - Verify results
   - Test rollback

5. **Document results**
   - If successful: Skill is ready
   - If issues: Fix and retest

## Summary

**Key Workflows:**

1. **Using skills:** Load → Apply → Follow patterns
2. **Adding skills:** Plan → Create → Document → Commit
3. **Modifying skills:** Read → Improve → Test → Update docs
4. **Combining skills:** Load multiple → Integrate → Apply consistently
5. **Maintaining skills:** Review → Update → Test → Document

**Best Practices:**

- Always follow the complete workflow
- Don't skip steps (especially testing)
- Update documentation
- Commit with clear messages
- Test before deploying

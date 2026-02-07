# Troubleshooting & Maintenance

This guide covers error handling, troubleshooting, maintenance, and special considerations for the skills repository.

## Common Issues & Solutions

### Issue 1: Skill Not Loading

**Symptoms:**
- Claude doesn't apply skill patterns
- Skill content not recognized
- Parse errors

**Troubleshooting Steps:**

1. **Check file path**
   ```bash
   # Verify skill exists
   ls skills/skill-name/SKILL.md
   ```
   - Must be at `skills/skill-name/SKILL.md`
   - Not nested deeper
   - Correct spelling

2. **Verify YAML frontmatter syntax**
   ```yaml
   ---
   name: skill-name
   description: "Valid YAML string"
   ---
   ```
   - Must have opening `---`
   - Must have closing `---`
   - Quotes around description if contains special characters
   - No tabs (use spaces)

3. **Confirm markdown formatting**
   - Proper heading hierarchy (# → ## → ###)
   - Code blocks have language: ` ```php `
   - No corrupted characters
   - Valid UTF-8 encoding

4. **Review for parsing errors**
   - Check for unclosed code blocks
   - Verify table formatting
   - Look for special characters

**Solution:**
```bash
# Validate YAML frontmatter
head -n 5 skills/skill-name/SKILL.md

# Check for markdown errors
# Use markdown linter if available
```

### Issue 2: Skill Producing Unexpected Results

**Symptoms:**
- Generated code doesn't match skill patterns
- Inconsistent outputs
- Missing best practices

**Troubleshooting Steps:**

1. **Re-read skill completely**
   - Don't skim
   - Read all sections
   - Note all patterns

2. **Check if context matches skill's intended use case**
   - Is the task within skill's scope?
   - Are you using the right skill?
   - Should you combine with another skill?

3. **Verify all skill patterns are being applied**
   - Check examples section
   - Review anti-patterns
   - Follow quick reference

4. **Ask user for clarification if ambiguous**
   ```
   "I've reviewed the [skill-name] skill. Before proceeding, I need clarification:
   - [Specific question about context]
   - [Specific question about approach]

   This will help me apply the skill's patterns most effectively."
   ```

### Issue 3: Multiple Applicable Skills

**Symptoms:**
- Two skills suggest different approaches
- Unclear which skill to use
- Conflicting patterns

**Resolution Steps:**

1. **Determine primary domain of the task**
   - What's the main focus?
   - Which skill is most specific?

2. **Load the most specific skill first**
   - Use the skill that directly addresses the task
   - Reference others as needed

3. **Combine patterns thoughtfully**
   - Use webapp-gui-design for UI layer
   - Use multi-tenant-saas-architecture for backend
   - Use mysql-best-practices for database

4. **If skills truly conflict, ask user**
   ```
   "I notice the [skill-1] and [skill-2] skills have different
   recommendations for [topic]. For your use case, I recommend [skill-1]
   because [reason]. Would you like me to proceed with that approach?"
   ```

### Issue 4: Skill Over 500 Lines

**Symptoms:**
- SKILL.md exceeds 500 lines
- Token inefficiency
- Hard to navigate

**Solution:**

1. **Move detailed content to subdirectories**
   ```
   skills/skill-name/
   ├── SKILL.md (trim to <500 lines)
   ├── references/
   │   ├── advanced-patterns.md
   │   └── troubleshooting.md
   └── examples/
       └── code-samples.php
   ```

2. **Keep only core patterns in SKILL.md**
   - Overview
   - Most common patterns (75-90% use cases)
   - Quick reference
   - Links to references/

3. **Update references in SKILL.md**
   ```markdown
   ## Advanced Patterns

   For advanced use cases, see:
   - `references/advanced-patterns.md`
   - `references/edge-cases.md`
   ```

4. **Verify line count**
   ```bash
   wc -l skills/skill-name/SKILL.md
   # Must be ≤ 500
   ```

### Issue 5: Broken Links in Skills

**Symptoms:**
- References to non-existent files
- Outdated URLs
- Cross-reference errors

**Solution:**

1. **Audit all links**
   ```bash
   # Find all markdown links
   grep -r "\[.*\](" skills/skill-name/
   ```

2. **Verify file references**
   - Check `references/` directory exists
   - Verify file names match links
   - Ensure paths are correct

3. **Test external URLs**
   - Visit each URL
   - Update if moved
   - Remove if dead

4. **Update cross-references**
   - Link to other skills correctly
   - Use relative paths
   - Verify target files exist

### Issue 6: Outdated Skill Patterns

**Symptoms:**
- Technology versions outdated
- Deprecated APIs referenced
- Examples don't work

**Solution:**

1. **Identify outdated sections**
   - Check technology versions
   - Review API documentation
   - Test examples

2. **Update to current best practices**
   - Upgrade technology versions
   - Update API calls
   - Modernize examples

3. **Test updated patterns**
   - Run examples
   - Verify they work
   - Check for edge cases

4. **Document changes**
   ```bash
   git commit -m "improve: update skill-name to [new-version/new-pattern]"
   ```

## Maintenance Procedures

### Regular Maintenance Schedule

**Monthly:**
- [ ] Check all skills for line count (<500)
- [ ] Review examples for accuracy
- [ ] Test links (internal and external)
- [ ] Update technology versions

**Quarterly:**
- [ ] Full skill audit
- [ ] Update outdated patterns
- [ ] Refactor oversized files
- [ ] Review user feedback

**Before Project Handoff:**
- [ ] Complete skill audit
- [ ] Update all examples
- [ ] Verify all links work
- [ ] Document current state

**When Skills Feel "Heavy":**
- [ ] Immediate refactor
- [ ] Check line counts
- [ ] Move content to subdirectories
- [ ] Update TOC structure

### Skill Grooming Checklist

Run this checklist periodically:

#### Content Quality
- [ ] Remove outdated information
- [ ] Update examples to current patterns
- [ ] Verify all examples work
- [ ] Consolidate duplicate content
- [ ] Add missing examples

#### Structure Quality
- [ ] Check line counts (all <500)
- [ ] Verify heading hierarchy
- [ ] Ensure tables are well-formatted
- [ ] Check code blocks have language specified
- [ ] Confirm proper list formatting

#### Link Quality
- [ ] Test all internal links
- [ ] Verify external URLs
- [ ] Update moved content links
- [ ] Remove dead links
- [ ] Add missing cross-references

#### Documentation Quality
- [ ] Update README.md if needed
- [ ] Sync PROJECT_BRIEF.md
- [ ] Update cross-references
- [ ] Document deprecations
- [ ] Add migration guides if needed

### Version Control Best Practices

**Commit Messages:**

```bash
# Adding new skill
git commit -m "feat: add [skill-name] skill for [purpose]"

# Improving existing skill
git commit -m "improve: enhance [skill-name] with [addition]"

# Fixing skill issues
git commit -m "fix: correct [issue] in [skill-name]"

# Updating documentation
git commit -m "docs: update README with [changes]"

# Deprecating skill
git commit -m "deprecate: mark [skill-name] as deprecated, use [new-skill] instead"
```

**Branch Strategy:**

```
main                    # Stable, tested skills
├── skill/[name]       # New skill development
├── improve/[name]     # Skill improvements
└── docs/[change]      # Documentation updates
```

## Special Considerations

### When Users Fork This Repo

Users may fork to customize skills for their needs.

**Claude should:**

1. **Respect their customizations**
   - Don't override their changes
   - Work with their version
   - Apply their patterns

2. **Suggest merging improvements back upstream**
   - If they create valuable patterns
   - If they fix bugs
   - If they add missing features

3. **Maintain compatibility with standard skills**
   - Keep core structure
   - Follow naming conventions
   - Use standard frontmatter

### Cross-Platform Considerations

Skills should work across:

- **Operating Systems:** Windows, macOS, Linux
- **Tech Stacks:** JS, Python, PHP, Go, etc.
- **Project Scales:** Startup to enterprise

**Guidelines:**

1. **Keep skills framework-agnostic where possible**
   - Focus on patterns, not specific tools
   - Provide examples for multiple frameworks when relevant

2. **Clearly specify requirements**
   - If skill requires specific OS: Document it
   - If skill needs certain tools: List them
   - If skill assumes tech stack: State it

3. **Provide alternatives**
   - Windows vs Linux commands
   - Different language implementations
   - Framework variations

### Multi-Tenant Skill Usage

When using multi-tenant-saas-architecture or similar:

**Always:**
- Include tenant_id in all queries
- Filter data by tenant
- Enforce tenant isolation
- Test cross-tenant security

**Never:**
- Query without tenant filter
- Share data across tenants
- Bypass tenant checks
- Assume single tenant

### Security Skill Enforcement

**vibe-security-skill is MANDATORY for web work:**

Always apply alongside:
- webapp-gui-design
- api-design-patterns
- Any frontend work
- Any backend API work
- Any user input handling

**Security principles enforced:**
- Input validation
- Output escaping
- SQL injection prevention
- XSS protection
- CSRF protection
- Authentication security
- Authorization checks

### Database Skill Enforcement

**mysql-best-practices is MANDATORY for database work:**

**ALWAYS use for:**
- Database migrations
- Schema design
- Stored procedures
- Query optimization
- Index creation

**Migration checklist MUST be followed:**
- Grep codebase before changes
- Test on copy first
- Document rollback
- Export schema after
- Test all endpoints

## Error Prevention

### Pre-Commit Checks

Before committing any skill:

```bash
# 1. Check line count
wc -l skills/*/SKILL.md
# All must be ≤ 500

# 2. Validate YAML frontmatter
head -n 5 skills/*/SKILL.md
# Check for valid YAML

# 3. Test examples (if applicable)
# Run code examples to verify they work

# 4. Check for broken links
grep -r "\[.*\](" skills/
# Verify all referenced files exist

# 5. Run markdown linter (if available)
# Check formatting
```

### Code Review Checklist

When reviewing skill changes:

- [ ] Line count under 500
- [ ] Valid YAML frontmatter
- [ ] Examples are complete and working
- [ ] No hardcoded credentials
- [ ] No security vulnerabilities
- [ ] Proper markdown formatting
- [ ] Links work
- [ ] Cross-references correct
- [ ] Documentation updated

## Recovery Procedures

### Recovering from Bad Commit

```bash
# View commit history
git log --oneline

# Revert specific commit
git revert <commit-hash>

# Or reset to previous state (use carefully)
git reset --hard <previous-commit-hash>

# Push fix
git push origin main
```

### Restoring Deleted Skill

```bash
# Find deleted file in history
git log --all --full-history -- skills/skill-name/SKILL.md

# Restore from specific commit
git checkout <commit-hash> -- skills/skill-name/SKILL.md

# Commit restoration
git add skills/skill-name/SKILL.md
git commit -m "restore: recover skill-name from accidental deletion"
```

### Fixing Corrupted Skill

```bash
# Check git history for last good version
git log --oneline skills/skill-name/SKILL.md

# Show content at specific commit
git show <commit-hash>:skills/skill-name/SKILL.md

# Restore good version
git checkout <commit-hash> -- skills/skill-name/SKILL.md
```

## Monitoring & Analytics

### Track Skill Usage

If implementing usage tracking:

```markdown
# Usage Log (YYYY-MM)

## Most Used Skills
1. mysql-best-practices (45 uses)
2. webapp-gui-design (38 uses)
3. multi-tenant-saas-architecture (32 uses)

## Least Used Skills
1. gis-mapping (2 uses)
2. skill-writing (1 use)

## Action Items
- Consider deprecating rarely used skills
- Improve documentation for popular skills
- Create missing skills based on common requests
```

### Quality Metrics

Track skill quality:

```markdown
# Skill Quality Report (YYYY-MM)

## Line Count Compliance
- ✅ 12 skills under 500 lines
- ⚠️ 2 skills over 500 lines (need refactoring)

## Documentation Quality
- ✅ All have valid frontmatter
- ✅ 90% have working examples
- ⚠️ 10% have outdated examples

## Link Health
- ✅ 95% internal links work
- ⚠️ 5% broken links (need fixing)
```

## Summary

**Key Troubleshooting Points:**

1. **Skill not loading:** Check path, YAML, markdown
2. **Unexpected results:** Re-read skill, verify context
3. **Multiple skills:** Choose most specific
4. **Over 500 lines:** Move to subdirectories
5. **Broken links:** Audit and fix
6. **Outdated:** Update and test

**Maintenance Schedule:**

- **Monthly:** Basic checks
- **Quarterly:** Full audit
- **Before handoff:** Complete review
- **When heavy:** Immediate refactor

**Prevention:**

- Pre-commit checks
- Code review checklist
- Regular maintenance
- Quality tracking

**Remember:** Skills are living documents. Regular maintenance keeps them valuable and effective.

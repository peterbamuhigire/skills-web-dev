# Skill Authoring Best Practices

This guide covers practical decisions for writing concise, reliable Skills that Claude can discover and use effectively.

## Contents

- Core principles
- Degrees of freedom
- Testing by model
- Skill structure and frontmatter rules
- Naming conventions
- Writing effective descriptions
- Progressive disclosure patterns
- Avoid deeply nested references
- Longer reference files and tables of contents
- Workflows and feedback loops
- Content guidelines
- Common patterns
- Evaluation and iteration
- Observing real Skill usage
- Anti-patterns to avoid
- Advanced: Skills with executable code
- Package dependencies
- Runtime environment
- MCP tool references
- Avoid assuming tools are installed
- Technical notes
- Checklist for effective Skills

## Core principles

### Concise is key

The context window is shared by the system prompt, conversation history, other Skills’ metadata, and the user’s request. Once SKILL.md is loaded, every token competes for space.

**Default assumption: Claude is already very smart.** Only add context Claude does not already know. Challenge each paragraph:

- Does Claude really need this?
- Can I assume Claude knows this?
- Does this paragraph justify its token cost?

**Concise example (about 50 tokens):**

## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

**Too verbose (about 150 tokens):**

## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...

The concise version assumes Claude already understands PDFs and libraries.

## Degrees of freedom

Match the level of specificity to the task’s fragility and variability.

**High freedom (text-based instructions)**

Use when:

- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

Example:

## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions

**Medium freedom (pseudocode or scripts with parameters)**

Use when:

- A preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

Example:

## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```

**Low freedom (specific scripts, few or no parameters)**

Use when:

- Operations are fragile and error-prone
- Consistency is critical
- A specific sequence must be followed

Example:

## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add flags.

**Analogy**: A narrow bridge needs guardrails (low freedom). An open field allows many paths (high freedom).

## Testing by model

Skills act as additions to models, so test with every model you plan to use:

- **Claude Haiku (fast, economical)**: Does the Skill provide enough guidance?
- **Claude Sonnet (balanced)**: Is the Skill clear and efficient?
- **Claude Opus (powerful reasoning)**: Does the Skill avoid over-explaining?

What works perfectly for Opus may need more detail for Haiku.

## Skill structure and frontmatter rules

### YAML frontmatter

SKILL.md frontmatter requires two fields:

- `name`
  - Maximum 64 characters
  - Lowercase letters, numbers, and hyphens only
  - No XML tags
  - Cannot contain reserved words: "anthropic", "claude"
- `description`
  - Must be non-empty
  - Maximum 1024 characters
  - No XML tags
  - Must describe what the Skill does and when to use it

### SKILL.md body

Keep the body focused on core instructions and link to references for details.

## Naming conventions

Use consistent naming patterns. Prefer gerund form (verb + -ing):

**Good:**

- processing-pdfs
- analyzing-spreadsheets
- managing-databases
- testing-code
- writing-documentation

**Acceptable alternatives:**

- pdf-processing (noun phrase)
- process-pdfs (action-oriented)

**Avoid:**

- helper, utils, tools
- documents, data, files
- anthropic-helper, claude-tools
- Inconsistent patterns across your Skill collection

Consistent naming makes Skills easier to reference, understand, organize, and search.

## Writing effective descriptions

The `description` field drives Skill discovery. Write in third person and include both what the Skill does and when to use it.

**Good:** "Processes Excel files and generates reports"

**Avoid:**

- "I can help you process Excel files"
- "You can use this to process Excel files"

Be specific and include trigger terms.

**Good examples:**

PDF Processing skill:
"Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."

Excel Analysis skill:
"Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files."

Git Commit Helper skill:
"Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes."

**Avoid vague descriptions:**

- "Helps with documents"
- "Processes data"
- "Does stuff with files"

## Progressive disclosure patterns

SKILL.md is an overview that points to detailed materials as needed. Keep SKILL.md under 500 lines and split content into separate files when approaching that limit.

### Pattern 1: High-level guide with references

---

name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction
---

# PDF Processing

## Quick start

Extract text with pdfplumber:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

### Pattern 2: Domain-specific organization

Organize by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

SKILL.md:

# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution → See [reference/marketing.md](reference/marketing.md)

## Quick search

Find specific metrics using grep:

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```

### Pattern 3: Conditional details

Show basic content and link to advanced content:

# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)

## Avoid deeply nested references

Keep references one level deep from SKILL.md. Do not chain references through multiple files.

**Bad:** SKILL.md → advanced.md → details.md

**Good:** SKILL.md → advanced.md, reference.md, examples.md (each linked directly)

## Longer reference files and tables of contents

For references longer than 100 lines, include a table of contents at the top so Claude can see the full scope during partial reads.

Example:

# API Reference

## Contents

- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup

...

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. Provide a checklist Claude can copy and track.

Example 1: Research synthesis workflow (no code)

## Research synthesis workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. Where do sources agree or disagree?

**Step 3: Cross-reference claims**

Verify each major claim appears in source material and note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:

- Main claim
- Supporting evidence
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Confirm every claim references the correct source. If citations are incomplete, return to Step 3.

Example 2: PDF form filling workflow (with code)

## PDF form filling workflow

Copy this checklist and check off items:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.

### Implement feedback loops

Use the pattern: run validator → fix errors → repeat.

Example 1: Style guide compliance (no code)

## Content review process

1. Draft content using STYLE_GUIDE.md
2. Review against the checklist:
   - Terminology consistency
   - Examples match the standard format
   - Required sections present
3. If issues found:
   - Note each issue with section reference
   - Revise content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document

Example 2: Document editing process (with code)

## Document editing process

1. Edit `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message
   - Fix issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document

## Content guidelines

### Avoid time-sensitive information

Do not include information that will become outdated.

**Bad:**

If you're doing this before August 2025, use the old API.
After August 2025, use the new API.

**Good (use an "old patterns" section):**

## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>

### Use consistent terminology

Choose one term and use it throughout.

**Good (consistent):**

- Always "API endpoint"
- Always "field"
- Always "extract"

**Bad (inconsistent):**

- Mix "API endpoint", "URL", "API route", "path"
- Mix "field", "box", "element", "control"
- Mix "extract", "pull", "get", "retrieve"

## Common patterns

### Template pattern

Provide templates for output format, matching strictness to requirements.

**Strict requirement example:**

## Report structure

ALWAYS use this exact template:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```

**Flexible guidance example:**

## Report structure

Here is a sensible default format, but use best judgment:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on discovery]

## Recommendations
[Tailor to the specific context]
```

Adjust sections as needed for the analysis type.

### Examples pattern

Provide input/output pairs when output quality depends on examples.

## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:

```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:

```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:

```
chore: update dependencies and refactor error response format

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation.

### Conditional workflow pattern

Guide through decision points:

## Document modification workflow

1. Determine modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete

If workflows grow large, move them into separate files and direct Claude to read the correct file based on the task.

## Evaluation and iteration

### Build evaluations first

Create evaluations before extensive documentation:

1. Identify gaps: Run Claude on representative tasks without a Skill. Document failures.
2. Create evaluations: Build three scenarios that test the gaps.
3. Establish baseline: Measure performance without the Skill.
4. Write minimal instructions: Add only what is needed to pass evaluations.
5. Iterate: Execute evaluations, compare to baseline, refine.

**Evaluation structure:**

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate PDF processing library or command-line tool",
    "Extracts text content from all pages in the document without missing any pages",
    "Saves the extracted text to a file named output.txt in a clear, readable format"
  ]
}
```

There is no built-in evaluator; users can create their own evaluation system.

### Develop Skills iteratively with Claude

Use two instances:

- **Claude A**: Helps design and refine the Skill
- **Claude B**: Tests the Skill in real tasks

**Creating a new Skill:**

1. Complete a task without a Skill using Claude A.
2. Identify the reusable pattern (context, rules, assets).
3. Ask Claude A to create a Skill capturing the pattern.
4. Review for conciseness and remove unnecessary explanations.
5. Improve information architecture (split references if needed).
6. Test on similar tasks with Claude B.
7. Iterate based on observations.

**Iterating on an existing Skill:**

- Test real tasks with Claude B
- Observe errors or omissions
- Return to Claude A with specifics
- Apply refinements
- Test again

### Gathering team feedback

Share Skills with teammates and incorporate feedback:

- Does the Skill activate when expected?
- Are instructions clear?
- What is missing?

## Observing real Skill usage

Watch how Claude navigates Skills:

- Unexpected exploration paths (may signal structure issues)
- Missed connections (links not prominent enough)
- Overreliance on one file (move key content into SKILL.md)
- Ignored content (remove or re-signal it)

The `name` and `description` are critical for discovery. Ensure they clearly describe what the Skill does and when to use it.

## Anti-patterns to avoid

### Avoid Windows-style paths

Always use forward slashes:

✓ Good: scripts/helper.py, reference/guide.md
✗ Avoid: scripts\helper.py, reference\guide.md

### Avoid offering too many options

Provide a default and an escape hatch instead of a long list:

**Bad:** "Use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good:** "Use pdfplumber for text extraction. For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."

## Advanced: Skills with executable code

### Solve, don’t punt

Handle error conditions instead of failing and asking Claude to fix it.

**Good:**

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""
    except PermissionError:
        print(f"Cannot access {path}, using default")
        return ""
```

**Bad:**

```python
def process_file(path):
    return open(path).read()
```

### Avoid voodoo constants

Justify configuration parameters so Claude knows why they exist.

**Good:**

```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**Bad:**

```python
TIMEOUT = 47
RETRIES = 5
```

### Provide utility scripts

Pre-made scripts are more reliable and save tokens.

**Make execution intent clear:**

- Execute: "Run analyze_form.py to extract fields"
- Read: "See analyze_form.py for the field extraction algorithm"

Example:

## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output format:

```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
```

Returns: "OK" or lists conflicts

**fill_form.py**: Apply field values to PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```

### Use visual analysis

When inputs can be rendered as images, have Claude analyze them.

1. Convert PDF to images:

   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. Analyze each page image to identify form fields

### Create verifiable intermediate outputs

Use plan → validate → execute with a machine-verifiable plan file.

Example workflow:

- Analyze
- Create changes.json
- Validate changes.json
- Execute
- Verify output

Validation scripts should provide specific error messages like:
"Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed"

## Package dependencies

Skills run in environments with different constraints:

- **claude.ai**: Can install from npm, PyPI, and GitHub
- **Anthropic API**: No network access, no runtime package installation

List required packages in SKILL.md and verify availability.

## Runtime environment

Skills run with filesystem access, bash commands, and code execution tools.

How Claude accesses Skills:

- **Metadata pre-loaded**: name and description from frontmatter
- **Files read on-demand**: SKILL.md and references loaded when needed
- **Scripts executed efficiently**: can run without reading full contents
- **No context penalty for large files** until read

Guidelines:

- Use forward slashes in paths
- Name files descriptively: form_validation_rules.md, not doc2.md
- Organize by domain or feature
- Bundle large resources without context cost
- Prefer scripts for deterministic operations
- Make execution intent clear
- Test navigation paths with real requests

Example:

bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md

When the user asks about revenue, Claude reads reference/finance.md only.

## MCP tool references

If a Skill uses MCP tools, always use fully qualified tool names:

Format: ServerName:tool_name

Examples:

- BigQuery:bigquery_schema
- GitHub:create_issue

Without the server prefix, Claude may fail to locate the tool.

## Avoid assuming tools are installed

Be explicit about dependencies:

**Bad:** "Use the pdf library to process the file."

**Good:**

Install required package: `pip install pypdf`

Then use it:

```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```

## Technical notes

### YAML frontmatter requirements

- `name`: Maximum 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words
- `description`: Maximum 1024 characters, non-empty, no XML tags

### Token budgets

Keep SKILL.md body under 500 lines. Split to references when needed.

## Checklist for effective Skills

### Core quality

- Description is specific and includes key terms
- Description includes both what the Skill does and when to use it
- SKILL.md body is under 500 lines
- Additional details are in separate files (if needed)
- No time-sensitive information (or in "old patterns" section)
- Consistent terminology throughout
- Examples are concrete, not abstract
- File references are one level deep
- Progressive disclosure used appropriately
- Workflows have clear steps

### Code and scripts

- Scripts solve problems rather than punt to Claude
- Error handling is explicit and helpful
- No "voodoo constants"
- Required packages listed and verified as available
- Scripts have clear documentation
- No Windows-style paths (use forward slashes)
- Validation/verification steps for critical operations
- Feedback loops included for quality-critical tasks

### Testing

- At least three evaluations created
- Tested with Haiku, Sonnet, and Opus
- Tested with real usage scenarios
- Team feedback incorporated (if applicable)

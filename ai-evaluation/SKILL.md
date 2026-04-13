---
name: ai-evaluation
description: Use when setting up quality assurance for AI features — defining evaluation
  criteria, measuring output quality, using AI-as-judge, monitoring production AI,
  detecting drift, and building user feedback loops
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Evaluation and Monitoring

<!-- dual-compat-start -->
## Use When

- Use when setting up quality assurance for AI features — defining evaluation criteria, measuring output quality, using AI-as-judge, monitoring production AI, detecting drift, and building user feedback loops
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-evaluation` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Overview

Evaluation is the biggest bottleneck to successful AI deployment. Define evaluation criteria BEFORE building. Without evaluation, you cannot know if your AI feature is working, degrading, or harming users.

**Core principle:** Evaluation-driven development. Like TDD for AI — define what "good" means first, then build.

---

## Evaluation Dimensions

| Dimension | What to Measure | Method |
|---|---|---|
| **Format** | Is output valid JSON/schema? Correct length? | Automated rules |
| **Factual accuracy** | Does output match the provided context? | AI-as-judge or RAG citation check |
| **Safety** | Toxic, harmful, or brand-risk content? | Classifier or AI-as-judge |
| **Instruction-following** | Did it follow format/tone/language rules? | Automated + AI-as-judge |
| **Relevance** | Does output address the user's question? | AI-as-judge |
| **Cost** | Tokens per request; cost per feature | Logged automatically |
| **Latency** | Time to first token; total response time | Logged automatically |

---

## Evaluation Workflow

```
1. Define criteria before building
2. Create golden test set (20–50 examples with expected outputs)
3. Run automated format checks on every new model/prompt version
4. Run AI-as-judge for quality checks
5. Compare against previous version — only deploy if metrics hold or improve
6. Monitor production: track live metrics + user feedback
7. Retrain/reprompt when drift detected
```

---

## Creating a Golden Test Set

```sql
CREATE TABLE ai_eval_cases (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  feature_name    VARCHAR(100),       -- 'invoice_analysis', 'sales_report'
  input           TEXT NOT NULL,      -- the user query or document
  expected_output TEXT,               -- ideal output (or key elements of it)
  eval_criteria   JSON,               -- {"format": "json", "must_contain": ["total", "vendor"]}
  created_by      INT,
  created_at      TIMESTAMP DEFAULT NOW()
);
```

Build test cases from:
1. Real production queries (once live)
2. Domain expert-crafted examples
3. Edge cases: empty input, wrong language, very long input, adversarial input

---

## Automated Evaluation (No LLM Cost)

Run these on every deployment:

```php
class AiEvaluator {
    public function evaluateFormat(string $output, array $criteria): EvalResult {
        $score = 0;
        $issues = [];

        // JSON validity
        if (($criteria['format'] ?? null) === 'json') {
            $decoded = json_decode($output, true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                $issues[] = 'Invalid JSON';
            } else {
                $score += 25;
                // Required keys
                foreach ($criteria['required_keys'] ?? [] as $key) {
                    if (!array_key_exists($key, $decoded)) {
                        $issues[] = "Missing key: $key";
                    } else {
                        $score += 10;
                    }
                }
            }
        }

        // Length constraints
        if (isset($criteria['max_words'])) {
            $wordCount = str_word_count($output);
            if ($wordCount > $criteria['max_words']) {
                $issues[] = "Too long: {$wordCount} words (max {$criteria['max_words']})";
            } else {
                $score += 15;
            }
        }

        // Must-contain terms
        foreach ($criteria['must_contain'] ?? [] as $term) {
            if (stripos($output, $term) === false) {
                $issues[] = "Missing expected term: $term";
            } else {
                $score += 10;
            }
        }

        return new EvalResult($score, $issues);
    }
}
```

---

## AI-as-Judge

Use a strong model to evaluate your AI feature's outputs. Reliable for quality, relevance, and tone.

```php
function judgeAiOutput(string $input, string $output, string $criteria): array {
    $judgePrompt = <<<PROMPT
You are evaluating the quality of an AI assistant's response.

Evaluation criteria:
{$criteria}

User input:
---
{$input}
---

AI response to evaluate:
---
{$output}
---

Score the response on each criterion from 1–5 (5 = excellent).
Explain your reasoning briefly, then give an overall score (1–5).
Format your response as JSON:
{
  "relevance": {"score": X, "reason": "..."},
  "accuracy": {"score": X, "reason": "..."},
  "tone": {"score": X, "reason": "..."},
  "overall": X
}
PROMPT;

    return callLLM('gpt-4o', $judgePrompt, temperature: 0.1);
}
```

**AI-judge best practices:**
- Use a stronger model as judge than the one being evaluated
- Ask for reasoning BEFORE score (reduces positional bias)
- Use pairwise comparison (A vs B) for relative quality rather than absolute scores
- Multiple judges + average for high-stakes decisions
- Watch for self-serving bias (GPT-4 favours GPT-4 outputs)

---

## Production Monitoring

### Metrics to Track Per Feature

```sql
CREATE TABLE ai_quality_metrics (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id      INT NOT NULL,
  feature_name   VARCHAR(100),
  prompt_version VARCHAR(10),
  model          VARCHAR(50),
  format_valid   BOOLEAN,
  latency_ms     INT,
  tokens_in      INT,
  tokens_out     INT,
  judge_score    DECIMAL(3,2),         -- 1.00–5.00 from AI judge (async)
  user_rating    TINYINT,              -- 1–5 from explicit feedback
  thumbs_up      BOOLEAN,              -- quick user feedback
  created_at     TIMESTAMP DEFAULT NOW(),
  INDEX idx_feature_date (feature_name, created_at),
  INDEX idx_tenant_date (tenant_id, created_at)
);
```

### Key Metrics by Priority

1. **Format failure rate** — % of responses failing JSON/schema validation
2. **User thumbs-down rate** — explicit negative feedback
3. **Early termination rate** — user stops generation mid-way
4. **Average judge score** — from async AI-as-judge on random sample
5. **p50/p90/p99 latency** — track at percentiles, not average
6. **Cost per request** — tokens × price per token

### Alerting Thresholds

```php
$alerts = [
    'format_failure_rate' => 0.05,    // Alert if > 5% of responses fail format
    'thumbs_down_rate'    => 0.15,    // Alert if > 15% negative feedback
    'p99_latency_ms'      => 8000,    // Alert if p99 latency > 8 seconds
    'cost_per_request'    => 0.05,    // Alert if avg cost > $0.05 per request
];
```

---

## Drift Detection

Drift = your AI feature is silently getting worse. Causes:
1. **Model API updates** — providers silently update model versions
2. **System prompt edits** — even small changes change behaviour
3. **User behaviour shift** — users learn to write differently over time
4. **Data drift** — RAG documents become stale

### Detection

```sql
-- Weekly average quality score — watch for downward trend
SELECT
    YEARWEEK(created_at) AS week,
    feature_name,
    AVG(judge_score) AS avg_quality,
    AVG(CASE WHEN thumbs_up = FALSE THEN 1 ELSE 0 END) AS negative_rate,
    AVG(latency_ms) AS avg_latency
FROM ai_quality_metrics
WHERE tenant_id = ? AND created_at > DATE_SUB(NOW(), INTERVAL 8 WEEK)
GROUP BY week, feature_name
ORDER BY week;
```

**Act when:**
- Average quality score drops > 0.5 points vs last 4-week average
- Format failure rate doubles vs baseline
- User negative feedback rate increases > 5% week-over-week

---

## User Feedback Signals

| Signal | Type | Strength |
|---|---|---|
| Thumbs up / down | Explicit | Medium |
| Star rating | Explicit | Medium |
| "That's wrong" in chat | Implicit | High |
| User edits output | Implicit | Very high |
| Early generation stop | Implicit | Medium |
| Rephrases same question | Implicit | High |
| Regenerates response | Implicit | Medium |

**Collect user edits as preference data:** original output = rejected, edited version = preferred.

---

## Evaluation Before vs After Deployment

| Phase | What to Evaluate | How |
|---|---|---|
| **Pre-deploy** | New prompt version vs old | A/B on golden test set |
| **Pre-deploy** | New model vs old | Same test set, compare scores |
| **Post-deploy** | Production quality | Sample 5% of requests → AI judge |
| **Post-deploy** | User satisfaction | Feedback collection |
| **Ongoing** | Drift detection | Weekly metric trend |

**Never deploy a new prompt or model without running the golden test set first.**

---

## Anti-Patterns

- **No golden test set** — you cannot measure regression
- **Only measuring average latency** — track p90/p99; outliers hurt users
- **Skipping evaluation to ship faster** — silent quality degradation is worse than delay
- **No prompt versioning** — you cannot roll back a broken prompt
- **Judge uses same model as evaluated** — self-serving bias inflates scores
- **No user feedback mechanism** — your most valuable signal goes uncollected

---

## Sources
Chip Huyen — *AI Engineering* (2025) Ch.3–4,10; Chip Huyen — *Designing ML Systems* (2022) Ch.8

# When ML vs LLM vs Rules

Deciding which technique fits a SaaS feature. Wrong choice is the most expensive early mistake.

## Decision matrix

| Signal shape | Best fit | Typical SaaS examples |
| --- | --- | --- |
| Numeric features, labelled history, < 100 features | Tabular ML | Churn, demand forecast, credit score, late-payment risk, inventory reorder quantity |
| Free text, images, audio, PDFs | LLM or pre-trained model | Invoice extraction, sentiment, support triage, summary of meeting notes |
| Problem statable in < 5 boolean conditions | Rules in PHP | "Flag invoice if amount > 1M and supplier new" |
| Text in, number/label out | LLM -> ML hybrid | LLM extracts features from complaint text, GBDT classifies severity |
| Number in, narrative out | ML -> LLM hybrid | Forecast yields values, LLM drafts commentary for the CFO |

## Concrete SaaS scenarios

### Churn prediction (ML wins)
- 50+ numeric features per tenant (usage, invoices paid, support tickets, days since last login).
- Labelled data from historic cancellations.
- Need a calibrated probability for segmentation and CS outreach.
- Gradient-boosted trees. Retrain monthly.

### Support ticket triage (LLM wins)
- Input is free-text.
- Classes drift (new product means new tags).
- LLM zero-shot or few-shot outperforms a trained classifier until you have 5K+ labelled tickets.
- Once you have labels, add a small ML classifier as a cheaper fast path, with LLM as fallback.

### Duplicate customer detection (Rules or ML)
- If you can enumerate match rules (same phone, same TIN, fuzzy name match > 0.9), rules win.
- When signal needs to combine 8+ features with thresholds, a logistic or tree-based model beats hand-coded rules.

### Demand forecasting (ML / statistical wins)
- Univariate or low-dimensional time series.
- Prophet or SARIMA. LLM forecasting is expensive and unreliable for numeric series.

### Fraud flagging (Hybrid)
- Rules fire first for known bad patterns (blocklists, geo anomalies).
- IsolationForest on embeddings of transactions catches the weird cases.
- LLM reads the description field for prompt-injection / social-engineering indicators.

## Cost model

### Per-inference cost
- **Rules (PHP)**: sub-millisecond, essentially zero.
- **Tabular ML sidecar**: 1 to 50 ms CPU, no external call. Cost = server time only.
- **LLM call**: 200 ms to 5 s, $0.0001 to $0.05 per call depending on tokens and model. Network dependency.

Rule of thumb: if you'll score > 10K items a day, every unit of ML per-call cost matters. LLM quickly dominates the budget.

### Training cost
- **Rules**: developer time only.
- **Tabular ML**: minutes on a worker box, negligible $.
- **LLM fine-tune**: $50 to $5000, plus labelled data.

### Operational cost
- **Rules**: highest readability, lowest monitoring need, easiest to change (but easiest to rot without tests).
- **ML**: needs drift monitoring, periodic retraining, explainability infra.
- **LLM**: needs prompt versioning, eval harness, provider outage handling, PII scrubbing, cost monitoring.

Do not pay ML operational tax for a problem rules would solve.

## Sequencing: start simple, upgrade when data earns it

1. **Rules first.** Ship a deterministic rule. Log the decision plus the features you would have used.
2. **Collect labels.** After 3 to 6 months of real traffic, you have a labelled dataset.
3. **Baseline model.** Train logistic regression on those labels. Compare vs rules on a holdout week.
4. **Upgrade if it wins.** Move to GBDT only if logistic beats rules by a meaningful margin on a business metric.
5. **LLM is the last tool, not the first,** for numeric predictions. It is the first tool for language.

If you cannot articulate what metric the upgrade should improve, you are not ready to upgrade.

## Hybrid patterns that work

### LLM as feature extractor, ML as decider
```text
raw text -> LLM (extract sentiment, topic, urgency as JSON) -> ML classifier
```
Good when you have lots of text and some labels. ML remains explainable and cheap; LLM is called once per new item.

### ML as candidate generator, LLM as ranker
```text
query -> ML retrieves top 100 candidates -> LLM re-ranks top 10 with reasons
```
Used in search, recommendations, document Q&A (RAG).

### Rules as guardrail around ML
```text
ML predicts -> rules override for known edge cases (whitelist, blocklist, regulatory)
```
Always layer rules on top of ML for decisions that carry legal risk (credit denial, suspension, refunds).

### ML for probability, rules for action
```text
ML -> probability score -> business rule decides action based on threshold and context
```
Keeps the ML model stable while product tunes thresholds by segment.

## Red flags that tell you the choice is wrong

- **Building ML but no labels exist.** You are fitting noise.
- **Using LLM to predict a number.** Costly, unstable, non-calibrated. Use ML.
- **Using rules for a 20-variable interaction.** Rules collapse; engineers fear to touch them.
- **Using LLM for high-volume inference** (> 100K/day) when ML would do. Budget will surprise you.
- **Using ML when the rule "Y if X > threshold" achieves 95% of the value.** Complexity tax not earned.

## Picking for our stack

Default order for any new predictive feature in a PHP + MySQL + mobile SaaS:

1. Can this be a rule in PHP? Ship it. Measure.
2. Do we have labelled data and numeric features? Build tabular ML in a Python sidecar.
3. Is the input unstructured (text, image, PDF)? LLM (see `ai-*` skills).
4. Hybrid if the problem straddles categories.

Companion skills:
- LLM path: `ai-llm-integration`, `ai-predictive-analytics`, `ai-cost-modeling`.
- ML path: the rest of this skill.
- Rules path: ordinary PHP plus `advanced-testing-strategy` for regression coverage.

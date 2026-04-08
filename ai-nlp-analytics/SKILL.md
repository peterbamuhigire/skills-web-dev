---
name: ai-nlp-analytics
description: Text analytics using LLM APIs — sentiment analysis, customer feedback classification, document entity extraction, multi-language support (English/Luganda/Swahili), feedback aggregation, and NLP feature implementation for PHP/Android/iOS. Sources...
---

# AI NLP Analytics

## What NLP Analytics Does

Natural Language Processing (NLP) analytics transforms unstructured text — feedback, comments, messages, documents, forms — into structured, actionable insights. Using LLM APIs, you can perform sophisticated NLP without training custom models.

**Use cases for SaaS products:**
- Analyse parent/patient/customer feedback automatically.
- Classify support tickets or complaints by type and urgency.
- Extract key entities from uploaded documents (invoices, receipts, forms).
- Summarise free-text notes into structured records.
- Detect sentiment in survey responses across thousands of users.

---

## Feature 1: Sentiment Analysis

Classify the emotional tone of text as Positive, Neutral, or Negative. Apply to: feedback forms, app reviews, survey responses, support messages.

### Prompt Template

```
You are a sentiment analysis engine for a business management system.
Classify the sentiment of each piece of text.

Input: array of { id, text, source, language }
Output — strict JSON array:
[
  {
    "id": <string>,
    "sentiment": "positive|neutral|negative",
    "intensity": "strong|moderate|mild",
    "key_phrase": "<the phrase that most drives the sentiment, max 8 words>",
    "language_detected": "<ISO 639-1 code>"
  }
]

Rules:
- Detect language automatically; do not require English input.
- Do not infer sentiment from punctuation alone — read meaning.
- If text is too short to judge (< 3 words), return sentiment: "neutral", intensity: "mild".
```

### Aggregation Query (PHP/Laravel)

```php
// Aggregate sentiment results by tenant for the dashboard
$summary = DB::table('nlp_results')
    ->where('tenant_id', $tenantId)
    ->where('period', $period)
    ->selectRaw('
        sentiment,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
    ')
    ->groupBy('sentiment')
    ->get();

// Store individual results
NLPResult::create([
    'tenant_id'   => $tenantId,
    'source_type' => 'parent_feedback',
    'source_id'   => $feedbackId,
    'sentiment'   => $result['sentiment'],
    'intensity'   => $result['intensity'],
    'key_phrase'  => $result['key_phrase'],
    'period'      => now()->format('Y-m'),
]);
```

### Dashboard Display

```
Feedback Sentiment — This Term
Positive  ████████████░░░░  74%  (148 responses)
Neutral   ███░░░░░░░░░░░░░  18%  (36 responses)
Negative  ██░░░░░░░░░░░░░░   8%  (16 responses)

Top Negative Themes:
- "Fees too high" (6 mentions)
- "Poor communication from teachers" (4 mentions)
- "Long waiting times at the clinic" (3 mentions)
```

---

## Feature 2: Text Classification

Categorise incoming text into predefined business categories. Apply to: support tickets, expense descriptions, complaint types, document types.

### Prompt Template

```
You are a text classification engine.
Classify each item into exactly one category from the provided list.

Categories: [<list from caller>]

Input: array of { id, text }
Output — strict JSON array:
[
  {
    "id": <string>,
    "category": "<one of the provided categories>",
    "confidence": "high|medium|low",
    "secondary_category": "<second best category or null>"
  }
]

If the text does not fit any category, use the category: "uncategorised".
```

### Domain Category Examples

**Support tickets (school):**
```
["Fee query", "Grade query", "Attendance query", "Technical issue",
 "Complaint — teacher", "Complaint — facilities", "Admission enquiry", "Other"]
```

**Expense classification (ERP):**
```
["Travel", "Accommodation", "Meals", "Office supplies", "IT equipment",
 "Professional services", "Utilities", "Marketing", "Miscellaneous"]
```

**Healthcare complaints:**
```
["Wait time", "Staff conduct", "Treatment quality", "Billing",
 "Facility cleanliness", "Medication", "Communication", "Other"]
```

### Bulk Classification Cost

Processing 500 support tickets per month:
- Input: ~200 tokens per ticket × 500 = 100,000 tokens
- Output: ~30 tokens per ticket × 500 = 15,000 tokens
- With Haiku: (100K × $0.80 + 15K × $4.00) / 1M = $0.08 + $0.06 = **$0.14/month**

---

## Feature 3: Named Entity Extraction

Pull structured data from free-form documents. Apply to: uploaded invoices, receipts, ID documents, lab reports, application forms.

### Prompt Template — Invoice Extraction

```
You are a document intelligence engine.
Extract structured data from the provided invoice or receipt text.

Output — strict JSON:
{
  "vendor_name": "<string or null>",
  "vendor_tin": "<string or null>",
  "invoice_number": "<string or null>",
  "invoice_date": "<YYYY-MM-DD or null>",
  "due_date": "<YYYY-MM-DD or null>",
  "currency": "<ISO 4217 code>",
  "subtotal": <float or null>,
  "tax_amount": <float or null>,
  "total_amount": <float or null>,
  "line_items": [
    { "description": "<string>", "quantity": <float>, "unit_price": <float>, "amount": <float> }
  ],
  "extraction_confidence": "high|medium|low",
  "flags": ["<any field that could not be reliably extracted>"]
}

If a field is not present in the document, return null.
Do not invent or guess values — only extract what is explicitly stated.
```

### Photo-to-Text Pipeline (Android/iOS)

```kotlin
// Android — OCR via ML Kit, then send text to AI Service
val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
recognizer.process(InputImage.fromBitmap(bitmap, 0))
    .addOnSuccessListener { visionText ->
        val extractedText = visionText.text
        viewModel.extractInvoiceData(extractedText)  // calls AI Service
    }
```

---

## Feature 4: Feedback Aggregation and Theme Detection

Identify recurring themes across large volumes of free-text feedback. Useful for end-of-term parent surveys, patient satisfaction, customer reviews.

### Prompt Template

```
You are a qualitative research analyst.
Read the following responses and identify the top themes expressed.

Responses: [<array of text responses>]

Output — strict JSON:
{
  "total_responses_analysed": <int>,
  "themes": [
    {
      "theme": "<short label, max 5 words>",
      "description": "<one sentence explaining the theme>",
      "frequency": "<approximate number of responses mentioning this>",
      "sentiment": "positive|negative|mixed",
      "representative_quotes": ["<verbatim quote 1>", "<verbatim quote 2>"]
    }
  ],
  "overall_summary": "<2–3 sentence executive summary>",
  "top_recommended_action": "<one sentence — most impactful thing to address>"
}

Identify 3–7 distinct themes. Do not overlap themes.
```

**Batch size guidance:** Process 30–50 responses per API call. For 500 responses, run 10–17 calls nightly.

---

## Feature 5: Multi-Language Support

East African clients write in English, Luganda, Swahili, and mixed code-switching. LLMs handle this natively — no translation step needed.

**In every NLP prompt, add:**
```
Language handling:
- Accept input in any language including Luganda, Swahili, and East African English varieties.
- Output must always be in [target_language — default English].
- Do not transliterate names or places.
```

**Detected language handling (PHP):**
```php
$languageDetected = $nlpResult['language_detected']; // 'lg' = Luganda, 'sw' = Swahili

// Store for analytics — track which languages clients use
NLPResult::create([
    'language' => $languageDetected,
    // ...
]);

// Show language breakdown on admin dashboard
// "Feedback received: 62% English | 24% Luganda | 14% Swahili"
```

---

## NLP Analytics Storage Schema

```sql
CREATE TABLE nlp_results (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id       BIGINT UNSIGNED NOT NULL,
    source_type     VARCHAR(64) NOT NULL,  -- 'feedback', 'ticket', 'invoice', 'survey'
    source_id       BIGINT UNSIGNED NOT NULL,
    nlp_task        VARCHAR(32) NOT NULL,  -- 'sentiment', 'classification', 'extraction', 'themes'
    result_json     JSON NOT NULL,
    sentiment       ENUM('positive','neutral','negative') NULL,
    category        VARCHAR(128) NULL,
    confidence      ENUM('high','medium','low') NULL,
    language        CHAR(5) NULL,
    period          CHAR(7) NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tenant_period  (tenant_id, period),
    INDEX idx_source         (source_type, source_id),
    INDEX idx_sentiment      (tenant_id, sentiment, period)
);
```

---

## Anti-Patterns

- Never run NLP on personal health data without DPPA-compliant scrubbing first.
- Never show verbatim quotes in theme reports without confirming the user has permission to see that feedback (RBAC check).
- Never classify into too many categories (> 10) — accuracy degrades.
- Never skip the validation step: parse the JSON output before storing it.
- Never run entity extraction on an image without OCR first — the model needs text input, not an image file, unless using a vision-capable model.

---

**See also:**
- `ai-feature-spec` — Prompt design standards and output validation
- `ai-security` — PII scrubbing before NLP on personal data
- `ai-predictive-analytics` — Structured data prediction (classification, regression)
- `ai-analytics-dashboards` — Displaying sentiment and theme analytics
- `ai-cost-modeling` — Token cost for batch NLP processing

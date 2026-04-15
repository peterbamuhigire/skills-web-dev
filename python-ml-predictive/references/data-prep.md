# Data Preparation

Leakage and sloppy splits invalidate every metric downstream. Treat prep as an engineering discipline.

## Splits

### IID tabular — random split
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,          # preserves class balance for classification
    random_state=42,
)
```
Use stratified split whenever the target is categorical. Stratify by the rare class.

### Time-series — time-based split only
```python
cutoff = "2025-10-01"
train = df[df["ds"] <  cutoff]
test  = df[df["ds"] >= cutoff]
```
Never shuffle. The model must be trained on the past and evaluated on the future. For CV, use `TimeSeriesSplit` or Prophet's rolling-origin `cross_validation`.

### Grouped data — GroupKFold
Per-tenant, per-customer, or per-device data must never leak identities across splits.
```python
from sklearn.model_selection import GroupKFold

gkf = GroupKFold(n_splits=5)
for train_idx, test_idx in gkf.split(X, y, groups=df["customer_id"]):
    ...
```
Same customer cannot appear in both train and test. Without this, a model memorises customer identity and looks deceptively good.

### Combined time + group (common in SaaS)
Split by time first, then verify no customer straddles the boundary for per-customer features. If they do, either drop the straddlers or use only history before the cutoff.

## Leakage prevention checklist

Run this before every training run:

- [ ] No target-derived feature. If predicting `invoice_paid`, "days late" is the label, not a feature.
- [ ] No aggregations that include the row being predicted. Use rolling windows that end **before** the prediction date.
- [ ] Preprocessing (scalers, encoders, imputers) fit **on train only**, applied to val/test.
- [ ] No future data in features. `order_amount_next_month` is a label candidate, not a feature.
- [ ] No post-prediction user actions as features unless the model is re-trained to reflect them with the correct time offset.
- [ ] Train, val, test have the same preprocessing code path (use `Pipeline`).
- [ ] Split **before** any feature engineering that depends on other rows.

The `Pipeline` + `ColumnTransformer` pattern is the single best defence:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

numeric = ["mrr", "logins_30d", "tickets_open"]
categorical = ["plan", "country"]

num_tf = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale",  StandardScaler()),
])
cat_tf = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("ohe",    OneHotEncoder(handle_unknown="ignore", min_frequency=10)),
])
prep = ColumnTransformer([("num", num_tf, numeric), ("cat", cat_tf, categorical)])

model = Pipeline([("prep", prep), ("clf", GradientBoostingClassifier(random_state=42))])
model.fit(X_train, y_train)
```

`fit` only sees train. `predict` applies the saved transformation. No code path can accidentally leak.

## Scaling

| Situation | Scaler |
| --- | --- |
| Gaussian-ish feature, few outliers | `StandardScaler` (zero mean, unit variance) |
| Heavy-tailed feature, outliers present (amounts, durations) | `RobustScaler` (median, IQR) |
| Bounded or sparse feature | `MinMaxScaler` or leave as-is |
| Tree-based model (GBDT, RF, XGBoost, LightGBM) | Scaling not required — skip it |

Linear models, SVMs, KNN, and neural networks need scaled inputs. Trees do not care.

Log-transform heavy-tailed numeric targets (revenue, amounts) before regression; exponentiate predictions back.

## Categorical encoding

| Encoding | When to use | Caveat |
| --- | --- | --- |
| `OneHotEncoder` | Cardinality < ~20, linear models, small datasets | Explodes with high cardinality |
| Ordinal / integer | Tree models only, ordered categories | Lies to linear models |
| Target encoding | High-cardinality (country, SKU, customer_id as feature) | High leakage risk — use CV within the encoder |
| Frequency / count encoding | High-cardinality, tree model | Simple, safe, surprisingly strong |
| Embedding | Neural networks only | Overkill for tabular |

For OneHot always set `handle_unknown="ignore"` and `min_frequency=10` so rare categories collapse into a shared bucket. New categories at serving time then do not crash.

Target encoding example (safe, with CV):
```python
from category_encoders import TargetEncoder
enc = TargetEncoder(cols=["country"], smoothing=10)
# Inside a CV loop, otherwise leakage
```

## Imbalanced data

Typical SaaS problems (churn, fraud, late payment) are 1% to 10% positive. Accuracy is useless here.

### Tactic 1 — Class weights (preferred, first choice)
```python
from sklearn.linear_model import LogisticRegression
LogisticRegression(class_weight="balanced", max_iter=1000)
```
Works for most sklearn classifiers. No data duplication. Keeps calibration reasonable.

### Tactic 2 — Threshold tuning
Keep the data as-is. After training, pick a decision threshold that meets your precision/recall target:
```python
probs = model.predict_proba(X_val)[:, 1]
# Find threshold where precision >= 0.8
```
Defaults (0.5) are almost always wrong for imbalanced problems.

### Tactic 3 — Downsample the majority
Fast, loses information, can hurt probability calibration.
```python
majority_sample = majority.sample(n=len(minority) * 3, random_state=42)
```

### Tactic 4 — SMOTE and friends (last resort)
Oversamples the minority by synthetic interpolation.
```python
from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)
```
Caveats:
- Only on training fold, never on val/test.
- Distorts calibration; re-calibrate with `CalibratedClassifierCV`.
- Weak on high-cardinality categoricals — encode first.
- In practice class_weight is usually as good and simpler.

## Missing values

| Strategy | When |
| --- | --- |
| Drop rows | Missingness < 1% and random |
| Median impute (numeric) | Non-random, moderate missingness |
| Mode impute (categorical) | Small cardinality |
| "Missing" as its own category | Missingness is informative |
| Add a `was_missing` indicator column | Missingness itself predicts the target |
| Model-based (kNN, Iterative) | High-value pipelines, small data |

Never impute with the mean for heavy-tailed features. Never impute before splitting.

## Feature engineering lifecycle

1. **Draft features from domain knowledge.** Sit with the business owner for 30 minutes. Capture ratios, deltas, counts, time-since, rolling windows.
2. **Build them in a pure function** that takes raw data and returns a feature frame. This function must run identically at training and serving time. Unit-test it.
3. **Version feature definitions.** If you change a feature's logic, treat it as a new feature (`logins_30d_v2`) until models have retrained.
4. **Audit at prediction time.** Log feature values per prediction. You will need them for debugging and drift monitoring.
5. **Drop features with no lift.** Use permutation importance; features that do nothing add serving latency and retraining cost.
6. **Feature store** is overkill for most SaaS; a shared Python module with typed builders is enough until you have 5+ models sharing features.

## Multi-tenant prep notes

- Include `tenant_id` as a categorical feature (frequency-encoded) when a single global model serves many tenants.
- Build features using per-tenant rolling windows, not global ones. A "top 10% of revenue" feature must be ranked within tenant.
- For cold-start tenants, impute with population means flagged by `is_new_tenant = 1`.
- When a tenant churns, exclude their future data from the training set, not their past.

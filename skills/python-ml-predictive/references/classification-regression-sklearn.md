# Classification and Regression with scikit-learn

Tabular ML for churn, risk, scoring, demand, price. Prefer gradient-boosted trees. Linear models as the baseline. Neural networks only when data volume and complexity justify them.

## The Pipeline + ColumnTransformer pattern

Every model must be wrapped in a `Pipeline` so preprocessing fits only on training data and serialises cleanly.

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import HistGradientBoostingClassifier

numeric = ["mrr", "logins_30d", "days_since_signup", "invoices_overdue"]
categorical = ["plan", "country", "industry"]

num_tf = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale",  StandardScaler()),
])
cat_tf = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("ohe",    OneHotEncoder(handle_unknown="ignore", min_frequency=10)),
])
prep = ColumnTransformer([
    ("num", num_tf, numeric),
    ("cat", cat_tf, categorical),
])

model = Pipeline([
    ("prep", prep),
    ("clf",  HistGradientBoostingClassifier(random_state=42)),
])
model.fit(X_train, y_train)
```

Benefits:
- No leakage: scaler and imputer learn from train only.
- One artifact to serialise (`joblib.dump(model, "churn_v3.joblib")`).
- Serving code is `model.predict_proba(X)` — no hand-rolled preprocessing.

For tree models (GBDT, RF, XGBoost, LightGBM) skip the `StandardScaler`; it is a no-op.

## Model selection order

Try in this order. Stop when a model is good enough and interpretable.

1. **Logistic Regression** (classification) / **Ridge / Lasso** (regression)
   - Fast, calibrated, coefficient-readable baseline.
   - Always include. Final metric must beat it.
2. **HistGradientBoostingClassifier / Regressor** (sklearn) or **LightGBM**
   - Usually the winner on tabular data.
   - Handles missing values natively.
3. **XGBoost**
   - Equivalent to LightGBM; pick based on ops familiarity.
4. **RandomForestClassifier / Regressor**
   - Try when GBDT is unstable (very noisy labels, few rows).
5. **Neural network (MLP)**
   - Only if: > 100K rows, heavy feature-engineering has diminishing returns, team has time and tooling.
   - Most SaaS tabular problems never need this.

### Rule of thumb
If logistic beats GBDT on a holdout, your feature set is weak or your data is tiny. Go back to features.

## GBDT choices

| Library | Strengths | Weaknesses |
| --- | --- | --- |
| `HistGradientBoostingClassifier` (sklearn) | No extra dependency, native missing-value handling, cat features (as of recent versions) | Slightly slower than LightGBM on large data |
| `lightgbm` | Fast, low memory, native categorical support | External dependency, version drift |
| `xgboost` | Very mature, GPU support, interoperable | Heavier API |
| `GradientBoostingClassifier` (old sklearn) | Legacy | Slow, avoid for new work |

For new projects in this stack, `HistGradientBoostingClassifier` is the default. Move to LightGBM if speed matters.

## Hyperparameter tuning

### RandomizedSearchCV first
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, loguniform

param_distributions = {
    "clf__learning_rate": loguniform(0.01, 0.3),
    "clf__max_iter": randint(100, 800),
    "clf__max_leaf_nodes": randint(15, 127),
    "clf__min_samples_leaf": randint(10, 200),
    "clf__l2_regularization": loguniform(1e-3, 1.0),
}

search = RandomizedSearchCV(
    model,
    param_distributions=param_distributions,
    n_iter=40,
    scoring="roc_auc",
    cv=5,
    n_jobs=-1,
    random_state=42,
)
search.fit(X_train, y_train)
print(search.best_params_, search.best_score_)
```

Start with `n_iter=20..50`. Only grid-search for the last 1–2 parameters after Random has narrowed ranges.

### Optuna (when Random is not enough)
```python
import optuna

def objective(trial):
    params = {
        "learning_rate": trial.suggest_float("lr", 0.01, 0.3, log=True),
        "max_leaf_nodes": trial.suggest_int("leaves", 15, 127),
        "min_samples_leaf": trial.suggest_int("min_leaf", 10, 200),
        "l2_regularization": trial.suggest_float("l2", 1e-3, 1.0, log=True),
    }
    clf = HistGradientBoostingClassifier(random_state=42, **params)
    # Evaluate via CV and return mean ROC-AUC
    ...
    return score

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100, timeout=1800)
```

Optuna's TPE sampler is more efficient than random for > 5 parameters. Budget by time, not trials.

### Budget rules
- First model: 30 min of CV search.
- Production retrain: 2–4 hr max. If it takes longer you are over-fitting to the search.
- Always hold out a final test set not touched by CV.

## Class imbalance

See `data-prep.md` for general tactics. In sklearn classifiers set `class_weight="balanced"`. In XGBoost/LightGBM use `scale_pos_weight = n_negative / n_positive`. Then tune the threshold, not the training data, when possible.

## Calibration

Probabilities from trees or SVMs are often mis-calibrated. If the UI shows "40% churn risk", that number must mean roughly 40% of such customers actually churn. Without calibration, the number is a ranking, not a probability.

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
calibrated.fit(X_train, y_train)
```

- `method="sigmoid"` (Platt) — for small data, smooth calibration.
- `method="isotonic"` — for larger data (> 10K rows), flexible but can overfit.

Verify with a calibration plot:
```python
from sklearn.calibration import CalibrationDisplay
CalibrationDisplay.from_estimator(calibrated, X_val, y_val, n_bins=10)
```
The line should hug the diagonal. See `explainability.md` for the visualisation.

## Regression specifics

- **Target transform.** Revenue and amount targets are heavy-tailed. Train on `log1p(y)`, predict, then `expm1(yhat)`. Better metrics and less skew.
- **Huber / Quantile loss.** For regressions with outliers, use `loss="absolute_error"` or Huber in sklearn GBR, or quantile regression for prediction intervals.
- **Prediction intervals.** Train three GBDT regressors at quantiles 0.1, 0.5, 0.9:
  ```python
  from sklearn.ensemble import GradientBoostingRegressor
  q_low = GradientBoostingRegressor(loss="quantile", alpha=0.1).fit(X, y)
  q_med = GradientBoostingRegressor(loss="quantile", alpha=0.5).fit(X, y)
  q_high = GradientBoostingRegressor(loss="quantile", alpha=0.9).fit(X, y)
  ```
  Display low/median/high in the UI.

## Multi-tenant patterns

- **Global model with `tenant_id` as a feature.** Start here. Use frequency or target encoding for tenant_id.
- **Per-tenant models** only when:
  - A tenant has > 10K labelled rows of its own.
  - Global model performance varies > 2x across tenants (audit with per-tenant metrics).
  - Business requires tenant-isolated training (data residency, sensitivity).
- **Cold start.** New tenant -> global model + `is_new_tenant = 1` flag, with conservative thresholds.

## Typical full workflow

```python
from pathlib import Path
import joblib

# 1. Split (see data-prep.md)
# 2. Build Pipeline with ColumnTransformer + HGB
# 3. Randomized search with CV on train only
# 4. Evaluate best on held-out test
# 5. Refit best pipeline on full train+val
# 6. Calibrate (optional, for probability-facing features)
# 7. Compute SHAP-based explanations on sample (see explainability.md)
# 8. Serialise

joblib.dump(best_model, Path("models") / "churn_v3.joblib")
```

## Anti-patterns

- Tuning on the test set.
- Searching 10K combinations to squeeze 0.2% ROC-AUC.
- Using accuracy on imbalanced data.
- Dropping the logistic baseline — you lose the "is this even working?" check.
- Feeding the raw dataframe to `predict` when training used a `Pipeline` — you bypass the prep.
- Retraining nightly by default. Retrain on a trigger.

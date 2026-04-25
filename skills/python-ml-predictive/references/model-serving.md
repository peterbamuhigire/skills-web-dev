# Model Serving

Lightweight serving for a PHP + MySQL + mobile SaaS. No MLflow or Kubeflow. FastAPI sidecar plus a worker for batch.

See `python-saas-integration` for the broader sidecar architecture.

## Serialisation — joblib

Joblib is the standard for sklearn, xgboost, lightgbm, Prophet (via its own method).

```python
from joblib import dump, load

dump(model, "churn_v3.joblib")        # save
model = load("churn_v3.joblib")       # load
```

Rules:
- Serialise the **whole `Pipeline`**, not just the final estimator. The preprocessing is part of the model.
- Include the feature list in the artifact (`model.feature_names_in_` is set automatically by sklearn when fit with a DataFrame).
- Do **not** pickle lambdas or closures. Use named functions.

### Pickle compatibility risks
Pickle is not stable across major package versions.

- Pin sklearn/xgboost/lightgbm versions in `pyproject.toml`.
- Record the versions inside the artifact:
  ```python
  artifact = {
      "model": model,
      "sklearn_version": sklearn.__version__,
      "xgboost_version": xgboost.__version__,
      "feature_names": list(X_train.columns),
      "trained_at": datetime.utcnow().isoformat(),
      "metrics": {"roc_auc": 0.82, "pr_auc": 0.55},
      "training_rows": len(X_train),
  }
  dump(artifact, "churn_v3.joblib")
  ```
- Retraining after a sklearn major upgrade is safer than loading an old artifact into a new runtime.

### Prophet
Prophet exposes its own JSON serialisation:
```python
from prophet.serialize import model_to_json, model_from_json
with open("prophet_v2.json", "w") as f:
    f.write(model_to_json(m))
```
Joblib works but JSON is more portable across Prophet versions.

## Artifact directory layout

Standard layout inside the Python service:

```text
src/
  service_name/
    ml/
      __init__.py
      features.py           # feature builders
      churn.py              # scoring wrapper
      demand.py
      artifacts/
        churn_v3.joblib
        churn_current -> churn_v3.joblib     # symlink
        demand_20260301.joblib
        demand_current -> demand_20260301.joblib
```

Rules:
- Filenames include semver (`_v3`) or date (`_20260301`).
- A symlink `<model>_current` points to the active version.
- Never overwrite an existing artifact. Write new, flip symlink.
- Artifacts **not in git**. Store in object store (S3, GCS) and download at container startup. `.gitignore` the `artifacts/` folder.

Download-at-startup pattern:
```python
# src/service_name/ml/bootstrap.py
import boto3, pathlib, os
def ensure_artifacts():
    client = boto3.client("s3")
    local = pathlib.Path("/app/src/service_name/ml/artifacts")
    local.mkdir(parents=True, exist_ok=True)
    for key in ["churn_current.joblib", "demand_current.joblib"]:
        dest = local / key
        if not dest.exists():
            client.download_file(os.environ["ML_BUCKET"], key, str(dest))
```

## Loading strategy — eager at startup

Load the model **once per process**, at import time or startup hook. Never per request.

```python
# src/service_name/ml/churn.py
from joblib import load
from pathlib import Path
from functools import lru_cache

MODEL_PATH = Path(__file__).parent / "artifacts" / "churn_current.joblib"

@lru_cache(maxsize=1)
def _bundle():
    return load(MODEL_PATH)

def score(features: dict) -> float:
    bundle = _bundle()
    X = build_feature_frame(features, bundle["feature_names"])
    return float(bundle["model"].predict_proba(X)[0, 1])
```

With FastAPI, prefer the lifespan context:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

ml_bundle = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_bundle["churn"] = load("artifacts/churn_current.joblib")
    yield

app = FastAPI(lifespan=lifespan)
```

## FastAPI /score endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

class ChurnRequest(BaseModel):
    tenant_id: int
    customer_id: int
    mrr: float
    logins_30d: int
    tickets_open: int
    plan: str
    country: str

class ChurnResponse(BaseModel):
    probability: float
    version: str
    reasons: list[str]

@app.post("/score/churn", response_model=ChurnResponse)
def score_churn(req: ChurnRequest):
    try:
        bundle = ml_bundle["churn"]
        X = build_feature_frame(req.model_dump(), bundle["feature_names"])
        p = float(bundle["model"].predict_proba(X)[0, 1])
        reasons = top_reasons(bundle, X)     # see explainability.md
        return ChurnResponse(probability=p, version=bundle["version"], reasons=reasons)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

Contract rules:
- Strict Pydantic input schema. No extras. Mismatched fields return 422.
- Always return `version`. The PHP caller logs it with the decision.
- Return `reasons` for high-stakes scores.
- Timeout at the gateway (200 ms sidecar budget is reasonable).

## Batch scoring in workers

Nightly churn scoring of all customers — a worker task, not a request.

```python
def nightly_churn_scoring():
    bundle = load("artifacts/churn_current.joblib")
    df = fetch_customers_df()
    X = build_feature_frame_batch(df, bundle["feature_names"])
    probs = bundle["model"].predict_proba(X)[:, 1]
    df["churn_score"] = probs
    df["scored_at"] = pd.Timestamp.utcnow()
    df["model_version"] = bundle["version"]
    write_scores_to_mysql(df[["tenant_id", "customer_id", "churn_score",
                              "scored_at", "model_version"]])
```

Batch beats per-request scoring whenever:
- Predictions do not need sub-minute freshness.
- Volume > a few thousand per day.
- PHP can read a `scores` table instead of calling the sidecar.

Write to MySQL with an index on `(tenant_id, scored_at)` for fast reads.

## Shadow mode / A-B

Before switching live:
1. Deploy new model as `churn_v4.joblib` alongside `churn_current`.
2. Score every request with both; return the current version's score to the UI.
3. Log both predictions with `request_id`, `version`, `score`.
4. After N days / N thousand requests, compare offline (agreement rate, calibration, lift).
5. Flip the symlink to `churn_v4.joblib`. Keep `churn_v3.joblib` on disk for rollback.

Code sketch:
```python
def score_shadow(features):
    p_live = _score_with(ml_bundle["churn_live"], features)
    p_shadow = _score_with(ml_bundle["churn_shadow"], features)
    log.info("shadow", live=p_live, shadow=p_shadow,
             version_live=ml_bundle["churn_live"]["version"],
             version_shadow=ml_bundle["churn_shadow"]["version"])
    return p_live
```

For true A/B with user impact, split by `tenant_id % 10`: buckets 0–7 get live, 8–9 get shadow as live; compare business KPI (retention) over weeks.

## Rollback plan

Rollback must be:
- **Fast**: flip symlink, restart service (< 1 min).
- **Tested**: include a rollback rehearsal before every major model push.
- **Reversible**: never delete the previous artifact.

Keep the last 3 versions on disk. CI prunes older ones.

## Versioning the contract

If feature names or order changes, bump the **input schema version** too. PHP must pass schema version so sidecar can route to the right pipeline or reject a stale client.

## Common failures

- **"Unknown category" at serving.** Encoder was fit with `handle_unknown="error"`. Always `"ignore"` in production.
- **Latency spikes.** Model loaded per request instead of eager. Profile with `py-spy`.
- **Silent drift.** Scores look fine, business KPI drops. You lacked monitoring — see `monitoring-and-drift.md`.
- **Stale features.** Request carries feature values computed hours ago. Add a `features_as_of` timestamp to the request.
- **OOM on restart.** Artifacts too large to fit in the container. Switch to lazy load, lighter model, or bigger instance.

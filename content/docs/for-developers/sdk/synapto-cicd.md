# synapto-cicd

Scores a CI/CD deployment for risk before it runs. Used by the Integration Layer to power the CI/CD Risk Assessment page (`/cicd`).

## Install

```bash
pip install -e libs/synapto-cicd
```

## Classes

### `CICDDeployment`

Input model:

| Field | Type | Description |
|-------|------|-------------|
| `service_name` | `str` | Name of the service being deployed |
| `environment` | `str` | `"development"`, `"staging"`, or `"production"` |
| `changed_files` | `list[str]` | List of changed file paths |
| `affected_services` | `list[str]` | Downstream services affected |
| `has_db_migration` | `bool` | Whether the deployment includes a DB schema migration |
| `is_off_hours` | `bool` | Whether deploying outside business hours |
| `rollback_available` | `bool` | Whether a tested rollback procedure exists |
| `commit_message` | `str \| None` | Optional commit message |

### `CICDRiskAssessment`

Output model:

| Field | Type | Description |
|-------|------|-------------|
| `risk_score` | `float` | 0.0–1.0 |
| `risk_level` | `str` | `"low"`, `"medium"`, `"high"`, or `"critical"` |
| `risk_factors` | `list[str]` | Human-readable list of contributing factors |
| `requires_manual_approval` | `bool` | True when `risk_score >= 0.6` |
| `recommendation` | `str` | One-sentence action recommendation |

### `CICDRiskScorer`

```python
from synapto_cicd import CICDRiskScorer, CICDDeployment

scorer = CICDRiskScorer()
result = scorer.score(CICDDeployment(
    service_name="api",
    environment="production",
    changed_files=["src/api.py", "migrations/0042.sql"],
    affected_services=["frontend", "worker"],
    has_db_migration=True,
    is_off_hours=False,
    rollback_available=True,
))
print(result.risk_score)   # e.g. 0.6
print(result.risk_level)   # "high"
print(result.risk_factors) # ["Production environment deployment", "Database migration included"]
```

## Risk factor weights

| Factor | Score contribution |
|--------|--------------------|
| Production environment | +0.30 |
| Database migration | +0.30 |
| Large changeset (>30 files) | +0.20 |
| Medium changeset (>10 files) | +0.10 |
| Off-hours deployment | +0.15 |
| No rollback available | +0.15 |
| >2 affected services | +0.10 |

Score is capped at 1.0. `APPROVAL_THRESHOLD = 0.6`.

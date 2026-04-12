# SDK Overview

`synapto-sdk` is a meta-package that aggregates all Synapto AIOps libraries under a single install. It is the recommended way to use the libraries outside of the core platform services.

## Install

```bash
pip install synapto-sdk
# or in editable mode from the repo:
pip install -e libs/synapto-sdk
```

Installing `synapto-sdk` pulls in:

| Library | Purpose |
|---------|---------|
| `synapto-contracts` | Shared Pydantic schemas (`AnomalySignal`, `IncidentClassification`, etc.) |
| `synapto-telemetry` | OTel-backed instrumentation emitter |
| `synapto-detector` | Statistical anomaly detection |
| `synapto-classifier` | 6-pass incident classification pipeline |
| `synapto-remediator` | Workflow resolution and safety gating |
| `synapto-cicd` | CI/CD risk scoring |

## Quick usage

```python
from synapto_sdk import CICDRiskScorer, TelemetryEmitter, ClassifierPipeline

# Score a deployment
scorer = CICDRiskScorer()

# Emit telemetry
emitter = TelemetryEmitter(service_name="my-service", host="host-01")
```

See individual library pages for detailed usage.

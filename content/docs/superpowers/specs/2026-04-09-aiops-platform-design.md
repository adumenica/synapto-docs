# AIOps Platform — Library-First Architecture Design

**Date:** 2026-04-09
**Status:** Approved
**Author:** Principal Software Architect (AI-assisted)
**Codebase:** Synapto — Self-Healing Infrastructure Platform

---

## 1. Context & Goals

Synapto is a working self-healing infrastructure platform with 9 FastAPI microservices, a Python edge agent (mTLS/gRPC), a shared AI client (Anthropic/OpenAI/Google), and a Redis Streams-based event pipeline. The platform already performs reactive remediation via policies + playbooks.

The goal of this design is to evolve Synapto into a full AIOps platform by adding:

1. **Proactive telemetry** — instrumentation embedded in every service and the edge agent
2. **Hybrid anomaly detection** — statistical always-on baseline, ML layer that promotes automatically
3. **Smarter incident classification + noise reduction** — library rules first, ML second, AI last
4. **Workflow-based remediation** — replacing policies + playbooks with a unified, non-technical-user-friendly workflow model
5. **Pre-deploy risk scoring** — a CI/CD library that gates deployments on live incident and anomaly data

### Core constraint

All capabilities are built as **independent, in-repo Python libraries** under `libs/`. No new microservices are introduced. The "platform" is the emergent result of these libraries running inside existing services.

The remediation philosophy is strictly **Library-First, AI-Fallback**: named catalogue actions are tried first, ML-matched historical workflows second, AI generation only when the catalogue has no answer.

---

## 2. Repository Structure

```
Synapto/
├── backend/                    # existing microservices (unchanged structure)
├── frontend/                   # existing React app
├── synapto-agent/              # existing edge agent
├── infrastructure/             # existing k8s/otel
│
└── libs/                       # NEW — AIOps library monorepo
    ├── synapto-contracts/      # Shared Pydantic data models — no logic, no deps
    ├── synapto-telemetry/      # OTel instrumentation for services + agent
    ├── synapto-detector/       # Hybrid anomaly detection
    ├── synapto-classifier/     # Incident classification + noise reduction
    ├── synapto-remediator/     # Workflow engine (library-first, AI fallback)
    ├── synapto-cicd/           # Pre-deploy risk scoring
    └── synapto-sdk/            # Meta-package: re-exports all five
```

Each library is a standalone Python package with its own `pyproject.toml`, installable via `pip install -e libs/<name>`. Services reference them in `requirements.txt` as path dependencies:

```
-e ../../libs/synapto-telemetry
-e ../../libs/synapto-remediator
```

### Dependency graph (strictly acyclic)

```
synapto-contracts   (no deps on other libs)
       ↑
synapto-telemetry   (depends on: contracts)
synapto-detector    (depends on: contracts, telemetry)
synapto-classifier  (depends on: contracts, detector)
synapto-remediator  (depends on: contracts, classifier)
synapto-cicd        (depends on: contracts, detector, classifier)
       ↑
synapto-sdk         (depends on: all five above)
```

No library imports from a sibling further down the chain. This rule is enforced by a CI lint step.

The existing `backend/shared/` module is **not replaced** — it retains auth, DB models, config, and crypto. The new libraries are additive.

---

## 3. `synapto-contracts` — Shared Data Layer

**Rule:** Zero business logic. Zero I/O. Zero external dependencies beyond `pydantic`. Every other library imports from here.

```
synapto-contracts/
└── synapto_contracts/
    ├── telemetry.py     # TelemetrySignal, Metric, LogRecord, Span
    ├── anomaly.py       # AnomalySignal, AnomalyScore, DetectionMethod
    ├── incident.py      # NormalizedIncident, IncidentClassification, NoiseVerdict
    ├── workflow.py      # Workflow, WorkflowStep, StepType, WorkflowResult
    ├── cicd.py          # DeploymentContext, RiskScore, RiskFactor
    └── __init__.py
```

### Key contracts

**`TelemetrySignal`** — universal envelope flowing edge → detector → classifier:

```python
class TelemetrySignal(BaseModel):
    signal_id: UUID
    source: str               # "synapto-agent", "integration-layer", etc.
    host: str
    service: Optional[str]
    timestamp: datetime
    metric: Optional[Metric]
    log: Optional[LogRecord]
    span: Optional[Span]
    labels: dict[str, str]
    tenant_id: Optional[UUID]
```

**`Workflow`** — the unified replacement for Policy + Playbook:

```python
class StepType(str, Enum):
    LIBRARY_ACTION = "library_action"   # named action from catalogue
    SCRIPT         = "script"           # raw script (advanced users)
    AI_GENERATE    = "ai_generate"      # AI fallback step
    NOTIFY         = "notify"           # alert/ticket creation
    CONDITION      = "condition"        # conditional branch

class WorkflowStep(BaseModel):
    name: str
    type: StepType
    action: Optional[str]       # e.g. "restart-service", "clear-disk-space"
    script: Optional[str]       # used when type=SCRIPT
    timeout_seconds: int = 60
    on_failure: Literal["abort", "continue", "fallback"] = "abort"

class WorkflowTrigger(BaseModel):
    field: str                  # e.g. "severity", "layer", "metric_name"
    operator: str               # "eq", "gte", "contains"
    value: str

class WorkflowCondition(BaseModel):
    field: str                  # e.g. "host", "labels.env"
    operator: str               # "eq", "neq", "contains", "gte", "lte"
    value: str

class Workflow(BaseModel):
    id: UUID
    name: str
    description: str
    trigger: WorkflowTrigger
    conditions: list[WorkflowCondition] = []
    steps: list[WorkflowStep]
    created_by: Optional[str]
    is_enabled: bool = True
```

`WorkflowTrigger` and `WorkflowCondition` use simple field/operator/value structures so the frontend renders them as form inputs — non-technical users never see raw JSON.

**`IncidentClassification`** — classifier output consumed by the remediator:

```python
class IncidentClassification(BaseModel):
    incident_id: UUID
    layer: InfraLayer           # OS, NETWORK, DATABASE, MIDDLEWARE, APPLICATION
    confidence: float           # 0.0–1.0
    method: Literal["rules", "ml", "ai"]
    is_duplicate: bool
    duplicate_of: Optional[UUID]
    noise_score: float          # 0.0 = definite incident, 1.0 = definite noise
    suggested_workflow_id: Optional[UUID]
```

**`RiskScore`** — CI/CD pre-deploy output:

```python
class RiskScore(BaseModel):
    score: float
    level: Literal["low", "medium", "high", "critical"]
    factors: list[RiskFactor]
    recommendation: Literal["proceed", "proceed_with_caution", "block"]
    summary: str                # human-readable, shown in CI output
```

---

## 4. `synapto-telemetry` — Instrumentation Library

```
synapto-telemetry/
└── synapto_telemetry/
    ├── instrument.py     # FastAPI auto-instrumentation decorator
    ├── emitter.py        # Core TelemetryEmitter class
    ├── exporters.py      # OTel exporter configuration (OTLP, stdout, Redis)
    ├── agent.py          # Lightweight emitter for synapto-agent (no FastAPI dep)
    ├── context.py        # Trace context propagation helpers
    └── __init__.py
```

### For backend microservices

```python
# main.py — two lines added, nothing else changes
from synapto_telemetry import instrument_service
instrument_service(app, service_name="orchestration-layer", export_to="otlp")
```

Auto-instruments all HTTP routes (latency, status codes, errors), adds a `/metrics` Prometheus-compatible endpoint, and emits `TelemetrySignal` objects to the configured exporter.

### For the edge agent

```python
from synapto_telemetry.agent import AgentTelemetryEmitter

emitter = AgentTelemetryEmitter(host=self.hostname, tenant_id=self.tenant_id)
emitter.emit_metric("disk.used_percent", value=82.4, labels={"mount": "/var"})
emitter.emit_log("nginx service failed to start", level="error", service="nginx")
```

The `AgentTelemetryEmitter` has no FastAPI dependency — it works in the plain Python agent process.

### Exporters

| Exporter | Use case |
|---|---|
| `OTLPExporter` | Production — sends to the OTel collector in `infrastructure/otel/` |
| `RedisExporter` | Fastest path — publishes `TelemetrySignal` JSON to a Redis Stream for the detector |
| `StdoutExporter` | Development and CI — structured JSON to stdout |

The `RedisExporter` reuses the existing Redis Streams infrastructure, meaning the detector receives telemetry in real-time with no new infrastructure.

### Trace context propagation

`context.py` injects `X-Synapto-Trace-ID` headers on inter-service calls so a full remediation chain (alert → classification → execution) appears as a single trace in any OTel-compatible backend.

The `infrastructure/otel/collector-config.yaml` is written as part of this library's integration, receiving OTLP from all instrumented services and routing to Prometheus and a trace backend (Grafana Tempo or Jaeger).

---

## 5. `synapto-detector` — Hybrid Anomaly Detection

```
synapto-detector/
└── synapto_detector/
    ├── detector.py          # AnomalyDetector — main entry point
    ├── statistical.py       # Z-score, moving average, rate-of-change
    ├── ml.py                # Isolation Forest + Prophet wrappers
    ├── window.py            # Sliding window state management
    ├── promoter.py          # Decides when to promote statistical → ML
    ├── store.py             # Detector state persistence (Redis + Postgres)
    ├── consumer.py          # Redis Streams background consumer
    └── __init__.py
```

### The two-layer model

**`StatisticalEngine`** — runs from day one, no historical data required:
- Z-score for point anomalies (sudden CPU spike)
- Moving average with dynamic threshold for trend anomalies (disk slowly filling)
- Rate-of-change for sudden drops (100 req/s → 0 instantly — service crash)
- Thresholds are per-signal, per-host, stored in Redis as sliding windows

**`MLEngine`** — activates automatically via `Promoter`:

```python
class Promoter:
    """
    Once MIN_SAMPLES observations are accumulated over MIN_DAYS for a signal,
    promotes that signal from StatisticalEngine to MLEngine.
    Demotes back if data gaps exceed 48 hours.
    """
    MIN_SAMPLES = 1000
    MIN_DAYS = 7
```

ML models:
- **Isolation Forest** (scikit-learn) — unsupervised multivariate anomaly detection, no labelled data required
- **Prophet** (Meta) — optional, for signals with known seasonality. Only loaded if `prophet` is installed.

### Usage

```python
from synapto_detector import AnomalyDetector

detector = AnomalyDetector(redis_url="redis://redis:6379", tenant_id=tenant_id)

# Inline evaluation
result = detector.evaluate(signal)   # returns AnomalySignal or None

# Background consumer (preferred for services)
await detector.start_consuming(stream="synapto:telemetry", on_anomaly=handle_anomaly)
```

The `consumer.py` module runs as a background task inside the existing `orchestration-layer` — no new service needed.

### `AnomalySignal` output

```python
class AnomalySignal(BaseModel):
    signal_id: UUID
    source_signal_id: UUID
    host: str
    metric_name: str
    observed_value: float
    expected_range: tuple[float, float]
    deviation_score: float          # 0.0–1.0
    detection_method: Literal["statistical", "ml"]
    severity: EventSeverity
    tenant_id: Optional[UUID]
    timestamp: datetime
    context: dict                   # window stats for explainability
```

The `context` field always carries the window statistics used to make the decision, providing human-readable explainability for every anomaly.

---

## 6. `synapto-classifier` — Incident Classification & Noise Reduction

```
synapto-classifier/
└── synapto_classifier/
    ├── classifier.py        # IncidentClassifier — main entry point
    ├── rules.py             # Rule-based classification engine
    ├── deduplicator.py      # Fingerprinting + correlation window
    ├── noise_filter.py      # Noise scoring (flapping, maintenance, low-confidence)
    ├── ml_classifier.py     # TF-IDF + cosine similarity on historical incidents
    ├── ai_classifier.py     # AI fallback (wraps existing AIClient)
    ├── fingerprint.py       # Deterministic incident fingerprinting
    └── __init__.py
```

### The five-pass pipeline

Every `AnomalySignal` passes through these stages in order, stopping as soon as a confident result is produced:

```
AnomalySignal
     │
     ▼
 [Pass 1] Noise Filter ──── noise_score > 0.75 ──► discard silently
     │
     ▼
 [Pass 2] Deduplicator ──── is_duplicate=True ──► suppress, link to parent
     │
     ▼
 [Pass 3] Rule Engine ──── confidence >= 0.8 ──► emit IncidentClassification
     │ (no match)
     ▼
 [Pass 4] ML Classifier ── confidence >= 0.65 ──► emit IncidentClassification
     │ (no match)
     ▼
 [Pass 5] AI Fallback ────────────────────────► emit IncidentClassification
                                                  (method="ai", always produces result)
```

### Pass 1 — Noise Filter

Three noise sources detected:
- **Flapping** — a signal that has fired and recovered more than N times in a rolling window
- **Maintenance windows** — signals from hosts tagged with an active maintenance label
- **Low-deviation anomalies** — `deviation_score < 0.2` signals assessed against the host's recent history

### Pass 2 — Deduplicator

Deterministic fingerprinting to identify the same incident arriving from multiple monitoring sources simultaneously:

```python
def compute_fingerprint(signal: AnomalySignal) -> str:
    key = f"{signal.host}:{signal.metric_name}:{signal.severity}:{floor_to_5min(signal.timestamp)}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]
```

Fingerprints stored in Redis with a configurable correlation window (default: 5 minutes).

### Pass 3 — Rule Engine

Rules defined as human-readable YAML, editable by non-technical users through the UI's rule builder:

```yaml
rules:
  - name: nginx-process-crash
    match:
      metric: process.active_count
      service: nginx
      deviation_score: ">= 0.9"
    classify:
      layer: MIDDLEWARE
      confidence: 0.95
      suggested_workflow: restart-nginx-workflow

  - name: disk-critical
    match:
      metric: disk.used_percent
      observed_value: ">= 90"
    classify:
      layer: OS
      confidence: 0.90
      suggested_workflow: clear-disk-workflow
```

### Pass 4 — ML Classifier

TF-IDF vectorization over historical `NormalizedIncident` titles and descriptions, with cosine similarity to find the closest past incident. Activates automatically once enough incidents accumulate (same promoter threshold as the detector). Copies `suggested_workflow_id` from the most similar historical incident.

### Pass 5 — AI Fallback

Calls existing `AIClient.analyze_incident()` from `shared/ai.py`. The `ai_client` is injected by the caller — not instantiated internally — keeping the library testable without an AI provider.

### Usage

```python
from synapto_classifier import IncidentClassifier

classifier = IncidentClassifier(
    redis_url="redis://redis:6379",
    rules_path="config/classification_rules.yaml",
    ai_client=ai_client,   # optional
    tenant_id=tenant_id,
)

result: IncidentClassification = await classifier.classify(anomaly_signal)

if result.is_duplicate or result.noise_score > 0.75:
    return  # suppress
# otherwise, pass to remediator
```

---

## 7. `synapto-remediator` — Workflow Engine

```
synapto-remediator/
└── synapto_remediator/
    ├── engine.py            # WorkflowEngine — main entry point
    ├── resolver.py          # Finds the right workflow for a classification
    ├── executor.py          # Executes a workflow step by step
    ├── catalogue.py         # Built-in library action registry
    ├── actions/
    │   ├── os.py            # restart-service, clear-disk, kill-process
    │   ├── network.py       # flush-dns, reset-interface, test-connectivity
    │   ├── database.py      # kill-long-queries, vacuum-table, restart-db
    │   ├── middleware.py    # restart-nginx, flush-redis-cache, restart-rabbitmq
    │   └── application.py  # scale-up, restart-pod, rotate-logs
    ├── ai_step.py           # AI_GENERATE step handler
    ├── notify_step.py       # NOTIFY step handler (ITSM, Slack, PagerDuty)
    ├── store.py             # Workflow persistence (load/save from DB)
    ├── audit.py             # Immutable execution audit log
    └── __init__.py
```

### The workflow resolution chain

```
IncidentClassification
        │
        ▼
[1] Exact match by suggested_workflow_id  ──► found ──► execute
        │ (not found)
        ▼
[2] Match by layer + labels in workflow catalogue
        │                         ──► found ──► execute
        │ (no match)
        ▼
[3] Match by similar past successful WorkflowResult
        │                         ──► found ──► execute
        │ (no match)
        ▼
[4] AI generates steps → executes → promotes to catalogue if successful
```

Steps 1–3 never call an AI provider. Step 4 fires only when the catalogue has no answer. On success, the AI-generated steps are promoted to a named workflow with `source="ai_promoted"` — the same incident pattern never reaches AI again.

### The action catalogue

Each action is a decorated function with a human-readable name, description, and parameter schema. The UI renders it as a searchable menu:

```python
@action(
    name="restart-nginx",
    description="Gracefully reload Nginx configuration and restart the service",
    layer=InfraLayer.MIDDLEWARE,
    params={"target_host": "The hostname to run this on"}
)
def restart_nginx(target_host: str, context: ActionContext) -> ActionResult:
    script = "sudo systemctl reload nginx || sudo systemctl restart nginx"
    return context.execute_script(script, language="bash", target=target_host)
```

Non-technical users building a workflow see **"Restart Nginx"** with a single field: *Target host*. No scripting or JSON required.

### Step failure semantics

| `on_failure` value | Behaviour |
|---|---|
| `"abort"` | Stop workflow, mark FAILED, emit NOTIFY step automatically |
| `"continue"` | Log failure, proceed to next step |
| `"fallback"` | Skip to the next AI_GENERATE or NOTIFY step |

### Audit log

Every step execution — inputs, outputs, exit code, duration, triggering actor — is written as an append-only record. Non-technical users see plain-English history: *"Step 2 of 3: Restart Nginx — completed in 4.2s on host web-01"*.

### Usage

```python
from synapto_remediator import WorkflowEngine

engine = WorkflowEngine(
    catalogue=ActionCatalogue(),
    execution_client=execution_engine_client,
    ai_client=ai_client,
    audit_log=AuditLog(db),
)

result: WorkflowResult = await engine.run(
    workflow=resolved_workflow,
    classification=classification,
    context={"target_host": "192.168.1.200", "tenant_id": tenant_id}
)
```

The engine calls the existing `execution-engine` service via HTTP for remote script execution — no change to the execution infrastructure.

---

## 8. `synapto-cicd` — Pre-Deploy Risk Scoring

```
synapto-cicd/
└── synapto_cicd/
    ├── scorer.py            # DeploymentRiskScorer — main entry point
    ├── analyzers/
    │   ├── diff.py          # Parses Git diff, identifies changed components
    │   ├── history.py       # Queries recent incidents for changed services
    │   ├── anomaly.py       # Checks active/recent anomalies on target hosts
    │   ├── topology.py      # Blast radius via NetworkTopology from knowledge-layer
    │   └── ai.py            # AI fallback for diff summarization
    ├── cli.py               # `synapto-risk` CLI command
    ├── github_action.py     # GitHub Actions output formatting
    ├── gitlab_ci.py         # GitLab CI output formatting
    └── __init__.py
```

### Scoring pipeline

Five analyzers contribute independently scored `RiskFactor` objects. Final score is a weighted sum (0.0–1.0):

| Analyzer | Weight | Logic |
|---|---|---|
| `RecentIncidentAnalyzer` | 0.30 | Incidents on changed services in the last 7 days |
| `ActiveAnomalyAnalyzer` | 0.25 | Active anomalies on target hosts right now |
| `BlastRadiusAnalyzer` | 0.20 | Downstream service count via NetworkTopology |
| `ChangeVolumeAnalyzer` | 0.15 | File count and service count in diff |
| `AIRiskAnalyzer` | 0.10 | AI diff summary — fires only when score is in ambiguous band [0.40, 0.65] |

A1–A4 are pure library logic, querying the Synapto DB and Redis. A5 never fires outside the ambiguous band.

### `DeploymentContext` input

```python
class DeploymentContext(BaseModel):
    git_sha: str
    git_diff_stat: str
    changed_services: list[str]
    target_environment: str
    target_hosts: list[str]
    deployer: str
    tenant_id: Optional[UUID]
```

### CI/CD integration

```bash
synapto-risk \
  --sha $GIT_SHA \
  --services "orchestration-layer,execution-engine" \
  --hosts "web-01,web-02" \
  --env production \
  --api-url http://synapto-api:8000 \
  --block-on high    # exit code 1 if score level >= high
```

GitHub Actions output formats the `RiskScore` as a PR comment with a colour-coded badge. No custom integration code needed.

### Post-deploy correlation loop

After a successful deployment, the scorer writes a `DeploymentRecord` (git SHA, services, timestamp) to Redis. The classifier's deduplicator reads these records — if an incident fires within 30 minutes of a deployment touching the same service, the `IncidentClassification` is automatically tagged `likely_caused_by_deploy: true`.

---

## 9. `synapto-sdk` — Meta-Package

A thin convenience package with no logic. Re-exports all five libraries and provides a `SynaptoSDK` bootstrap class:

```python
from synapto_sdk import SynaptoSDK

sdk = SynaptoSDK.from_env()   # reads REDIS_URL, DATABASE_URL, AI_PROVIDER, etc.

sdk.telemetry    # → TelemetryEmitter
sdk.detector     # → AnomalyDetector
sdk.classifier   # → IncidentClassifier
sdk.remediator   # → WorkflowEngine
sdk.cicd         # → DeploymentRiskScorer
```

Services needing only one library import it directly. The SDK is for `orchestration-layer` and `agent-service` which need the full pipeline.

---

## 10. Migration: Policies + Playbooks → Workflows

Migration is additive and non-breaking, executed in three phases.

**Phase 1 — Schema addition:** New `workflows` table added via Alembic migration. Existing `policies` and `playbooks` tables remain untouched.

**Phase 2 — Automated migration script:**

```
Policy.conditions  →  Workflow.trigger + Workflow.conditions
Policy.actions     →  Workflow.steps[0] (LIBRARY_ACTION or SCRIPT)
Playbook.steps     →  Workflow.steps[1..N]
```

Each migrated workflow gets `source="migrated_from_policy"` and `is_enabled=False`. An operator reviews and enables them one at a time through the UI.

**Phase 3 — Cutover:** Orchestration-layer switches its event consumer to call `WorkflowEngine.run()`. Old tables kept read-only for 30 days, then archived.

---

## 11. Platform Integration

Each existing microservice adopts only the libraries relevant to its responsibility:

| Service | Libraries adopted | What changes |
|---|---|---|
| `orchestration-layer` | `synapto-sdk` (full) | Replaces policy/playbook chain with `WorkflowEngine.run()`. Starts `AnomalyDetector` consumer as background task. |
| `integration-layer` | `synapto-telemetry` | `instrument_service(app)` added. Emits `TelemetrySignal` on every inbound event. |
| `execution-engine` | `synapto-telemetry` | `instrument_service(app)` added. Emits execution duration/outcome as metrics. |
| `knowledge-layer` | `synapto-telemetry` | `instrument_service(app)` added. Exposes workflow CRUD endpoints. |
| `learning-engine` | `synapto-telemetry` | `instrument_service(app)` added. Analytics endpoints query `WorkflowResult`. |
| `agent-service` | `synapto-telemetry` | `instrument_service(app)` added. |
| `synapto-agent` | `synapto-telemetry` (agent variant) | `AgentTelemetryEmitter` added to main agent loop. |
| **CI/CD pipelines** | `synapto-cicd` | `synapto-risk` CLI added as a pipeline step. |

---

## 12. Full Data Flow

```
[Host Metric / Alert]
        │
        ▼
synapto-agent  ──telemetry──►  Redis Stream: synapto:telemetry
        │                              │
integration-layer ──────────────────►  │
        │                              ▼
        │                    synapto-detector (in orchestration-layer)
        │                              │ AnomalySignal
        │                              ▼
        │                    synapto-classifier
        │                              │ IncidentClassification
        │                              ▼
        │                    synapto-remediator
        │                              │ WorkflowEngine.run()
        │                              ▼
        │                    execution-engine (existing)
        │                              │ WorkflowResult
        │                              ▼
        │                    audit log + learning loop (catalogue promotion)
        │
[CI Pipeline] ──► synapto-cicd ──► RiskScore ──► block / proceed
```

---

## 13. Out of Scope

The following are explicitly excluded from this design and should be addressed in separate specs:

- Frontend workflow builder UI (form-based editor for non-technical users)
- OTel collector backend selection and configuration (Grafana Tempo vs. Jaeger)
- Retraining pipeline for the ML classifier and detector models
- ITSM connector updates for the new `WorkflowResult` schema
- Multi-tenancy isolation for telemetry streams

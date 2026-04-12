# AIOps Missing Components Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the AIOps Library-First architecture by building `synapto-classifier`, `synapto-remediator`, `synapto-cicd`, `synapto-sdk`, and wiring telemetry instrumentation into all 7 uninstrumented services.

**Architecture:** Five independent tracks. Tracks 1 and 2 extract inline orchestration-layer logic into standalone `libs/` packages; Track 3 is a new CI/CD risk-scoring library; Track 4 is a dependency-free meta-package; Track 5 is mechanical — add `synapto-telemetry` to Dockerfiles and call `instrument_app()` in each service.

**Tech Stack:** Python 3.11, Pydantic v2, FastAPI, pytest, synapto-contracts (existing), synapto-telemetry (existing), httpx

---

## Files Overview

### Track 1 — `synapto-classifier`
- Create: `libs/synapto-classifier/pyproject.toml`
- Create: `libs/synapto-classifier/synapto_classifier/__init__.py`
- Create: `libs/synapto-classifier/synapto_classifier/noise_filter.py`
- Create: `libs/synapto-classifier/synapto_classifier/rule_engine.py`
- Create: `libs/synapto-classifier/synapto_classifier/safety_gate.py`
- Create: `libs/synapto-classifier/synapto_classifier/pipeline.py`
- Create: `libs/synapto-classifier/tests/test_noise_filter.py`
- Create: `libs/synapto-classifier/tests/test_rule_engine.py`
- Create: `libs/synapto-classifier/tests/test_safety_gate.py`
- Create: `libs/synapto-classifier/tests/test_pipeline.py`
- Modify: `backend/orchestration-layer/main.py` — remove inline classification helpers, import from `synapto_classifier`
- Modify: `backend/orchestration-layer/Dockerfile` — add `synapto-classifier` install

### Track 2 — `synapto-remediator`
- Create: `libs/synapto-remediator/pyproject.toml`
- Create: `libs/synapto-remediator/synapto_remediator/__init__.py`
- Create: `libs/synapto-remediator/synapto_remediator/models.py`
- Create: `libs/synapto-remediator/synapto_remediator/resolver.py`
- Create: `libs/synapto-remediator/synapto_remediator/engine.py`
- Create: `libs/synapto-remediator/tests/test_resolver.py`
- Create: `libs/synapto-remediator/tests/test_engine.py`
- Modify: `backend/orchestration-layer/main.py` — import `WorkflowResolver` from `synapto_remediator`
- Modify: `backend/orchestration-layer/Dockerfile` — add `synapto-remediator` install
- Modify: `backend/knowledge-layer/main.py` — add `is_gold_standard` field to Script model + PATCH endpoint
- Modify: `backend/shared/models.py` — add `is_gold_standard` column to Script table

### Track 3 — `synapto-cicd`
- Create: `libs/synapto-cicd/pyproject.toml`
- Create: `libs/synapto-cicd/synapto_cicd/__init__.py`
- Create: `libs/synapto-cicd/synapto_cicd/models.py`
- Create: `libs/synapto-cicd/synapto_cicd/scorer.py`
- Create: `libs/synapto-cicd/tests/test_scorer.py`
- Modify: `backend/api-gateway/main.py` — add `POST /api/v1/cicd/risk-assessment` proxy endpoint
- Modify: `backend/integration-layer/main.py` — add CI/CD webhook endpoint using `synapto_cicd`
- Modify: `backend/integration-layer/Dockerfile` — add `synapto-cicd` install

### Track 4 — `synapto-sdk`
- Create: `libs/synapto-sdk/pyproject.toml`
- Create: `libs/synapto-sdk/synapto_sdk/__init__.py`

### Track 5 — Service Instrumentation
- Modify: `backend/execution-engine/Dockerfile` + `backend/execution-engine/main.py`
- Modify: `backend/knowledge-layer/Dockerfile` + `backend/knowledge-layer/main.py`
- Modify: `backend/learning-engine/Dockerfile` + `backend/learning-engine/main.py`
- Modify: `backend/api-gateway/Dockerfile` + `backend/api-gateway/main.py`
- Modify: `backend/auth-service/Dockerfile` + `backend/auth-service/main.py`
- Modify: `backend/admin-service/Dockerfile` + `backend/admin-service/main.py`
- Modify: `backend/itsm-connector/Dockerfile` + `backend/itsm-connector/main.py`

---

## Track 1: `synapto-classifier` Library

### Task 1: Package scaffold + NoiseFilter (Pass 1)

**Files:**
- Create: `libs/synapto-classifier/pyproject.toml`
- Create: `libs/synapto-classifier/synapto_classifier/__init__.py`
- Create: `libs/synapto-classifier/synapto_classifier/noise_filter.py`
- Create: `libs/synapto-classifier/tests/__init__.py`
- Create: `libs/synapto-classifier/tests/test_noise_filter.py`

- [ ] **Step 1: Write the failing test**

```python
# libs/synapto-classifier/tests/test_noise_filter.py
import pytest
from datetime import datetime
from uuid import uuid4
from synapto_contracts import AnomalySignal, EventSeverity
from synapto_classifier.noise_filter import NoiseFilter, NoiseResult


def _signal(deviation_score: float) -> AnomalySignal:
    return AnomalySignal(
        signal_id=uuid4(),
        source_signal_id=uuid4(),
        host="web-01",
        metric_name="cpu_usage",
        observed_value=95.0,
        deviation_score=deviation_score,
        detection_method="statistical",
        severity=EventSeverity.HIGH,
        timestamp=datetime.now(),
    )


def test_high_deviation_scores_low_noise():
    result = NoiseFilter().evaluate(_signal(deviation_score=0.9))
    assert result.noise_score < 0.75
    assert result.should_discard is False


def test_low_deviation_scores_high_noise():
    result = NoiseFilter().evaluate(_signal(deviation_score=0.05))
    assert result.noise_score > 0.75
    assert result.should_discard is True


def test_medium_deviation_is_borderline():
    result = NoiseFilter().evaluate(_signal(deviation_score=0.3))
    assert 0.0 < result.noise_score < 1.0


def test_noise_result_has_reason_when_discarded():
    result = NoiseFilter().evaluate(_signal(deviation_score=0.05))
    assert result.discard_reason is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pip install -e ../synapto-contracts -e . 2>/dev/null
pytest tests/test_noise_filter.py -v
```

Expected: `ModuleNotFoundError: No module named 'synapto_classifier'`

- [ ] **Step 3: Create pyproject.toml**

```toml
# libs/synapto-classifier/pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "synapto-classifier"
version = "0.1.0"
description = "6-pass incident classification pipeline for Synapto AIOps"
requires-python = ">=3.9"
dependencies = [
    "synapto-contracts",
    "pydantic>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["synapto_classifier*"]
```

- [ ] **Step 4: Create `__init__.py` (empty for now)**

```python
# libs/synapto-classifier/synapto_classifier/__init__.py
from .noise_filter import NoiseFilter, NoiseResult
from .pipeline import ClassifierPipeline, ClassificationResult
```

Leave the pipeline import commented out until Task 4. Use this stub instead:

```python
# libs/synapto-classifier/synapto_classifier/__init__.py
from .noise_filter import NoiseFilter, NoiseResult
```

- [ ] **Step 5: Implement `noise_filter.py`**

```python
# libs/synapto-classifier/synapto_classifier/noise_filter.py
from pydantic import BaseModel
from typing import Optional
from synapto_contracts import AnomalySignal


class NoiseResult(BaseModel):
    noise_score: float          # 0.0 = definite incident, 1.0 = definite noise
    should_discard: bool
    discard_reason: Optional[str] = None


class NoiseFilter:
    """
    Pass 1: Computes a noise_score from deviation characteristics.
    Low deviation_score (small anomaly) = likely noise.
    Discards signals with noise_score > 0.75.
    """
    DISCARD_THRESHOLD = 0.75

    def evaluate(self, signal: AnomalySignal) -> NoiseResult:
        # Invert deviation_score: high deviation = low noise
        # deviation_score is 0.0-1.0; 0.0 means barely anomalous
        noise_score = max(0.0, 1.0 - (signal.deviation_score * 1.5))
        noise_score = min(noise_score, 1.0)

        should_discard = noise_score > self.DISCARD_THRESHOLD
        reason = (
            f"noise_score={noise_score:.2f} exceeds threshold {self.DISCARD_THRESHOLD} "
            f"(deviation_score={signal.deviation_score:.2f})"
            if should_discard else None
        )

        return NoiseResult(
            noise_score=round(noise_score, 4),
            should_discard=should_discard,
            discard_reason=reason,
        )
```

- [ ] **Step 6: Install and run tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pip install -e ../synapto-contracts -e .
pytest tests/test_noise_filter.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 7: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-classifier/
git commit -m "feat(classifier): scaffold synapto-classifier with Pass 1 NoiseFilter"
```

---

### Task 2: RuleEngine (Pass 3)

**Files:**
- Create: `libs/synapto-classifier/synapto_classifier/rule_engine.py`
- Create: `libs/synapto-classifier/tests/test_rule_engine.py`

- [ ] **Step 1: Write the failing test**

```python
# libs/synapto-classifier/tests/test_rule_engine.py
from datetime import datetime
from uuid import uuid4
from synapto_contracts import AnomalySignal, EventSeverity, InfraLayer
from synapto_classifier.rule_engine import RuleEngine, RuleResult


def _signal(metric_name: str, host: str = "web-01") -> AnomalySignal:
    return AnomalySignal(
        signal_id=uuid4(),
        source_signal_id=uuid4(),
        host=host,
        metric_name=metric_name,
        observed_value=95.0,
        deviation_score=0.9,
        detection_method="statistical",
        severity=EventSeverity.HIGH,
        timestamp=datetime.now(),
    )


def test_cpu_maps_to_os_layer():
    result = RuleEngine().classify(_signal("cpu_usage_percent"))
    assert result is not None
    assert result.layer == InfraLayer.OS
    assert result.confidence >= 0.8


def test_db_query_latency_maps_to_database():
    result = RuleEngine().classify(_signal("db_query_latency_ms"))
    assert result is not None
    assert result.layer == InfraLayer.DATABASE


def test_http_request_rate_maps_to_network():
    result = RuleEngine().classify(_signal("http_request_rate"))
    assert result is not None
    assert result.layer == InfraLayer.NETWORK


def test_unknown_metric_returns_none():
    result = RuleEngine().classify(_signal("totally_unknown_metric_xyz"))
    assert result is None


def test_high_confidence_signals_are_returned():
    result = RuleEngine().classify(_signal("memory_usage_bytes"))
    assert result is not None
    assert result.confidence >= 0.8
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/test_rule_engine.py -v
```

Expected: `ImportError: cannot import name 'RuleEngine'`

- [ ] **Step 3: Implement `rule_engine.py`**

```python
# libs/synapto-classifier/synapto_classifier/rule_engine.py
from typing import Optional
from pydantic import BaseModel
from synapto_contracts import AnomalySignal, InfraLayer

# Maps keyword fragments to (layer, confidence)
_RULES: list[tuple[list[str], InfraLayer, float]] = [
    (["cpu", "memory", "mem_", "swap", "load_avg", "disk_io", "kernel"],       InfraLayer.OS,          0.90),
    (["db_", "database", "query", "deadlock", "postgres", "mysql", "mongo"],    InfraLayer.DATABASE,    0.90),
    (["http", "request_rate", "latency", "dns", "network", "tcp", "socket"],    InfraLayer.NETWORK,     0.88),
    (["redis", "rabbitmq", "kafka", "queue", "nginx", "apache", "tomcat"],      InfraLayer.MIDDLEWARE,  0.85),
    (["app_", "error_rate", "response_time", "exception", "service_"],          InfraLayer.APPLICATION, 0.82),
]


class RuleResult(BaseModel):
    layer: InfraLayer
    confidence: float
    matched_rule: str


class RuleEngine:
    """
    Pass 3: Keyword-based classification.
    Returns a RuleResult with confidence >= 0.8 if a rule matches, else None.
    """
    CONFIDENCE_THRESHOLD = 0.8

    def classify(self, signal: AnomalySignal) -> Optional[RuleResult]:
        metric = signal.metric_name.lower()

        for keywords, layer, confidence in _RULES:
            for kw in keywords:
                if kw in metric:
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        return RuleResult(
                            layer=layer,
                            confidence=confidence,
                            matched_rule=kw,
                        )
        return None
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/test_rule_engine.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-classifier/
git commit -m "feat(classifier): add Pass 3 RuleEngine"
```

---

### Task 3: SafetyGate (Pass 6)

**Files:**
- Create: `libs/synapto-classifier/synapto_classifier/safety_gate.py`
- Create: `libs/synapto-classifier/tests/test_safety_gate.py`

- [ ] **Step 1: Write the failing test**

```python
# libs/synapto-classifier/tests/test_safety_gate.py
from synapto_classifier.safety_gate import SafetyGate


def test_rules_method_is_safe_by_default():
    safety = SafetyGate().evaluate(method="rules", steps=[], confidence=0.95)
    assert safety.requires_approval is False
    assert safety.is_safe_to_auto_run is True


def test_ai_method_with_destructive_keyword_requires_approval():
    steps = [{"name": "cleanup", "script_content": "rm -rf /var/log/*"}]
    safety = SafetyGate().evaluate(method="ai", steps=steps, confidence=0.85)
    assert safety.requires_approval is True
    assert safety.is_safe_to_auto_run is False


def test_ai_method_without_destructive_keywords_is_safe():
    steps = [{"name": "check logs", "script_content": "tail -n 100 /var/log/app.log"}]
    safety = SafetyGate().evaluate(method="ai", steps=steps, confidence=0.85)
    assert safety.requires_approval is False


def test_low_confidence_requires_approval():
    safety = SafetyGate().evaluate(method="ml", steps=[], confidence=0.60)
    assert safety.requires_approval is True


def test_confidence_at_threshold_is_approved():
    safety = SafetyGate().evaluate(method="ml", steps=[], confidence=0.70)
    assert safety.requires_approval is False


def test_risk_score_is_between_0_and_1():
    safety = SafetyGate().evaluate(method="ai", steps=[], confidence=0.5)
    assert 0.0 <= safety.risk_score <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/test_safety_gate.py -v
```

Expected: `ImportError: cannot import name 'SafetyGate'`

- [ ] **Step 3: Implement `safety_gate.py`**

```python
# libs/synapto-classifier/synapto_classifier/safety_gate.py
import re
from typing import List, Dict, Any, Literal
from synapto_contracts import RemediationSafety

_DESTRUCTIVE_PATTERNS = [
    r"rm\s+-rf",
    r"format\s+",
    r"mkfs",
    r"dd\s+if=/dev/zero",
    r"reboot",
    r"shutdown",
    r"DROP\s+TABLE",
    r"TRUNCATE",
    r"kill\s+-9\s+-1",
    r"iptables\s+-F",
]

MethodType = Literal["rules", "ml", "ai"]


class SafetyGate:
    """
    Pass 6: Final safety verdict.
    Rules: safe by default.
    AI: scan for destructive keywords.
    Low confidence (< 0.7): always requires approval.
    """
    CONFIDENCE_THRESHOLD = 0.70

    def evaluate(
        self,
        method: MethodType,
        steps: List[Dict[str, Any]],
        confidence: float,
    ) -> RemediationSafety:
        # Low confidence always requires approval
        if confidence < self.CONFIDENCE_THRESHOLD:
            return RemediationSafety(
                is_safe_to_auto_run=False,
                requires_approval=True,
                risk_score=round(1.0 - confidence, 2),
                risk_summary="Low classification confidence",
                approval_reason=f"Confidence {confidence:.2f} is below threshold {self.CONFIDENCE_THRESHOLD}",
            )

        # Rules-based match: safe by default
        if method == "rules":
            return RemediationSafety(
                is_safe_to_auto_run=True,
                requires_approval=False,
                risk_score=0.1,
                risk_summary="Library catalogue match — pre-approved",
            )

        # AI synthesis: scan for destructive keywords
        if method == "ai":
            found = []
            for step in steps:
                content = step.get("script_content") or ""
                for pattern in _DESTRUCTIVE_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        found.append(pattern)

            if found:
                return RemediationSafety(
                    is_safe_to_auto_run=False,
                    requires_approval=True,
                    risk_score=1.0,
                    risk_summary="AI-generated script contains destructive commands",
                    approval_reason=f"Destructive patterns found: {', '.join(found)}",
                )

        # ML or clean AI: approved
        return RemediationSafety(
            is_safe_to_auto_run=True,
            requires_approval=False,
            risk_score=0.2,
            risk_summary="Passed safety scan",
        )
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/test_safety_gate.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-classifier/
git commit -m "feat(classifier): add Pass 6 SafetyGate"
```

---

### Task 4: ClassifierPipeline (all 6 passes)

**Files:**
- Create: `libs/synapto-classifier/synapto_classifier/pipeline.py`
- Modify: `libs/synapto-classifier/synapto_classifier/__init__.py`
- Create: `libs/synapto-classifier/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# libs/synapto-classifier/tests/test_pipeline.py
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID
from synapto_contracts import AnomalySignal, EventSeverity, InfraLayer
from synapto_classifier.pipeline import ClassifierPipeline, ClassificationResult
from synapto_classifier.noise_filter import NoiseFilter
from synapto_classifier.rule_engine import RuleEngine
from synapto_classifier.safety_gate import SafetyGate


def _signal(deviation_score: float = 0.9, metric: str = "cpu_usage_percent") -> AnomalySignal:
    return AnomalySignal(
        signal_id=uuid4(),
        source_signal_id=uuid4(),
        host="db-01",
        metric_name=metric,
        observed_value=95.0,
        deviation_score=deviation_score,
        detection_method="statistical",
        severity=EventSeverity.HIGH,
        timestamp=datetime.now(),
    )


def _make_pipeline(duplicate_id: Optional[UUID] = None) -> ClassifierPipeline:
    def no_duplicate(s: AnomalySignal) -> Optional[UUID]:
        return duplicate_id

    return ClassifierPipeline(
        noise_filter=NoiseFilter(),
        rule_engine=RuleEngine(),
        safety_gate=SafetyGate(),
        duplicate_checker=no_duplicate,
    )


def test_noise_signal_is_discarded():
    pipeline = _make_pipeline()
    result = pipeline.classify(_signal(deviation_score=0.05))
    assert result.discarded is True
    assert result.classification is None


def test_real_signal_is_classified():
    pipeline = _make_pipeline()
    result = pipeline.classify(_signal(deviation_score=0.9, metric="cpu_usage_percent"))
    assert result.discarded is False
    assert result.classification is not None
    assert result.classification.layer == InfraLayer.OS
    assert result.classification.method == "rules"


def test_duplicate_signal_is_suppressed():
    existing_id = uuid4()
    pipeline = _make_pipeline(duplicate_id=existing_id)
    result = pipeline.classify(_signal(deviation_score=0.9))
    assert result.discarded is True
    assert result.discard_reason is not None
    assert "duplicate" in result.discard_reason.lower()


def test_classification_includes_safety():
    pipeline = _make_pipeline()
    result = pipeline.classify(_signal(deviation_score=0.9))
    assert result.classification is not None
    assert result.classification.safety is not None
    assert result.classification.safety.risk_score >= 0.0


def test_unknown_metric_falls_back_to_application_layer():
    pipeline = _make_pipeline()
    result = pipeline.classify(_signal(deviation_score=0.9, metric="totally_unknown_metric_xyz_abc"))
    assert result.discarded is False
    assert result.classification is not None
    assert result.classification.method in ("ml", "ai")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/test_pipeline.py -v
```

Expected: `ImportError: cannot import name 'ClassifierPipeline'`

- [ ] **Step 3: Implement `pipeline.py`**

```python
# libs/synapto-classifier/synapto_classifier/pipeline.py
from typing import Optional, Callable
from uuid import UUID
from pydantic import BaseModel
from synapto_contracts import AnomalySignal, IncidentClassification, InfraLayer, RemediationSafety

from .noise_filter import NoiseFilter
from .rule_engine import RuleEngine
from .safety_gate import SafetyGate


class ClassificationResult(BaseModel):
    classification: Optional[IncidentClassification] = None
    discarded: bool
    discard_reason: Optional[str] = None


class ClassifierPipeline:
    """
    6-Pass classification pipeline.

    Pass 1: Noise Filter      — discard noise_score > 0.75
    Pass 2: Deduplication     — suppress if duplicate_checker returns an existing ID
    Pass 3: Rule Engine       — classify if confidence >= 0.8
    Pass 4: ML Classifier     — classify if ml_classifier returns confidence >= 0.65
    Pass 5: AI Synthesis      — classify via ai_synthesizer (fallback, always returns)
    Pass 6: Safety Gate       — compute RemediationSafety for the chosen method

    Passes 4 and 5 accept optional callables; if None, falls through to the next pass.
    """

    def __init__(
        self,
        noise_filter: NoiseFilter,
        rule_engine: RuleEngine,
        safety_gate: SafetyGate,
        duplicate_checker: Optional[Callable[[AnomalySignal], Optional[UUID]]] = None,
        ml_classifier: Optional[Callable[[AnomalySignal], Optional[tuple]]] = None,
        ai_synthesizer: Optional[Callable[[AnomalySignal], tuple]] = None,
    ):
        self._noise = noise_filter
        self._rules = rule_engine
        self._safety = safety_gate
        self._dup_checker = duplicate_checker
        self._ml = ml_classifier
        self._ai = ai_synthesizer

    def classify(self, signal: AnomalySignal) -> ClassificationResult:
        # Pass 1: Noise Filter
        noise = self._noise.evaluate(signal)
        if noise.should_discard:
            return ClassificationResult(discarded=True, discard_reason=noise.discard_reason)

        # Pass 2: Deduplication
        if self._dup_checker:
            existing_id = self._dup_checker(signal)
            if existing_id:
                return ClassificationResult(
                    discarded=True,
                    discard_reason=f"duplicate of incident {existing_id}",
                )

        layer: Optional[InfraLayer] = None
        confidence: float = 0.0
        method: str = "ai"

        # Pass 3: Rule Engine
        rule_result = self._rules.classify(signal)
        if rule_result:
            layer = rule_result.layer
            confidence = rule_result.confidence
            method = "rules"

        # Pass 4: ML Classifier
        if layer is None and self._ml:
            ml_result = self._ml(signal)
            if ml_result and ml_result[1] >= 0.65:
                layer, confidence = ml_result
                method = "ml"

        # Pass 5: AI Synthesis (fallback — always produces a result)
        if layer is None:
            if self._ai:
                layer, confidence = self._ai(signal)
            else:
                layer = InfraLayer.APPLICATION
                confidence = 0.50
            method = "ai"

        # Pass 6: Safety Gate
        safety = self._safety.evaluate(method=method, steps=[], confidence=confidence)

        classification = IncidentClassification(
            incident_id=signal.signal_id,
            layer=layer,
            confidence=confidence,
            method=method,
            is_duplicate=False,
            noise_score=noise.noise_score,
            safety=safety,
        )

        return ClassificationResult(discarded=False, classification=classification)
```

- [ ] **Step 4: Update `__init__.py`**

```python
# libs/synapto-classifier/synapto_classifier/__init__.py
from .noise_filter import NoiseFilter, NoiseResult
from .rule_engine import RuleEngine, RuleResult
from .safety_gate import SafetyGate
from .pipeline import ClassifierPipeline, ClassificationResult
```

- [ ] **Step 5: Run all classifier tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-classifier
pytest tests/ -v
```

Expected: All 20 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-classifier/
git commit -m "feat(classifier): add ClassifierPipeline orchestrating all 6 passes"
```

---

### Task 5: Wire orchestration-layer to use synapto-classifier

**Files:**
- Modify: `backend/orchestration-layer/Dockerfile`
- Modify: `backend/orchestration-layer/main.py`

- [ ] **Step 1: Add install to Dockerfile**

In `backend/orchestration-layer/Dockerfile`, find the line that installs `synapto-contracts` and add `synapto-classifier` below it:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-detector && \
    pip install --no-cache-dir /app/libs/synapto-classifier
```

- [ ] **Step 2: Replace inline `execute_6_pass_pipeline` in main.py**

At the top imports section of `backend/orchestration-layer/main.py`, add after the existing lib imports:

```python
from synapto_classifier import ClassifierPipeline, NoiseFilter, RuleEngine, SafetyGate
from synapto_classifier.pipeline import ClassificationResult
```

Replace the body of `execute_6_pass_pipeline` (lines ~384–430) with:

```python
async def execute_6_pass_pipeline(incident_id: str, db: Session) -> Dict[str, Any]:
    """[ENTERPRISE] Delegates to synapto-classifier library."""
    import uuid
    incident = db.query(Incident).filter(Incident.id == uuid.UUID(incident_id)).first()
    if not incident:
        return {"success": False, "error": "Incident not found"}

    # Build a minimal AnomalySignal from the incident for classification
    from synapto_contracts import AnomalySignal, EventSeverity
    from datetime import datetime, timezone
    signal = AnomalySignal(
        signal_id=uuid.uuid4(),
        source_signal_id=uuid.UUID(incident_id),
        host=(incident.meta_data or {}).get("host", "unknown"),
        metric_name=incident.title,
        observed_value=0.0,
        deviation_score=0.9,  # Already determined anomalous at this point
        detection_method="statistical",
        severity=incident.severity,
        timestamp=datetime.now(timezone.utc),
        tenant_id=incident.tenant_id,
    )

    def dup_checker(s):
        # Delegate to existing deduplication helper
        import asyncio
        return None  # deduplication already done before pipeline is called

    pipeline = ClassifierPipeline(
        noise_filter=NoiseFilter(),
        rule_engine=RuleEngine(),
        safety_gate=SafetyGate(),
        duplicate_checker=dup_checker,
    )
    result = pipeline.classify(signal)

    if result.discarded:
        logger.info(f"[PIPELINE] Incident {incident_id} discarded: {result.discard_reason}")
        return {"success": False, "error": result.discard_reason}

    classification = result.classification
    meta = incident.meta_data.copy() if incident.meta_data else {}
    meta["layer"] = classification.layer.value
    meta["classification_method"] = classification.method
    meta["classification_confidence"] = classification.confidence
    meta["noise_score"] = classification.noise_score
    incident.meta_data = meta
    db.commit()

    # Routing path still uses existing helper
    routing_path = await calculate_routing_path(incident, db)
    meta["routing_path"] = routing_path
    incident.meta_data = meta
    db.commit()

    logger.info(f"[PIPELINE-COMPLETE] {incident_id} → layer={classification.layer.value}, method={classification.method}, routed={routing_path}")
    return {"success": True}
```

- [ ] **Step 3: Rebuild and verify container starts**

```bash
cd /Users/alind/Projects/Synapto
docker compose build orchestration-layer 2>&1 | tail -5
docker compose up -d orchestration-layer
sleep 5
docker logs synapto-orchestration-layer-7 --tail=10 2>&1
```

Expected: Logs show "Starting Orchestration Layer service" and no ImportError.

- [ ] **Step 4: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add backend/orchestration-layer/
git commit -m "feat(orchestration): delegate 6-pass pipeline to synapto-classifier library"
```

---

## Track 2: `synapto-remediator` Library

### Task 6: Package scaffold + WorkflowResolver models

**Files:**
- Create: `libs/synapto-remediator/pyproject.toml`
- Create: `libs/synapto-remediator/synapto_remediator/__init__.py`
- Create: `libs/synapto-remediator/synapto_remediator/models.py`
- Create: `libs/synapto-remediator/tests/__init__.py`
- Create: `libs/synapto-remediator/tests/test_resolver.py`

- [ ] **Step 1: Write failing test**

```python
# libs/synapto-remediator/tests/test_resolver.py
from synapto_remediator.models import (
    IncidentContext,
    Resolution,
    ResolutionMethod,
)


def test_incident_context_creation():
    ctx = IncidentContext(
        incident_id="abc-123",
        title="High CPU on web-01",
        sanitized_title="high cpu",
        os_family="linux",
        layer="os",
        tenant_id="tenant-1",
    )
    assert ctx.incident_id == "abc-123"
    assert ctx.os_family == "linux"


def test_resolution_has_method():
    res = Resolution(
        playbook_id="pb-1",
        playbook_steps=[{"name": "check cpu"}],
        method=ResolutionMethod.LIBRARY,
        was_generated=False,
    )
    assert res.method == ResolutionMethod.LIBRARY
    assert res.was_generated is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-remediator
pip install -e ../synapto-contracts -e . 2>/dev/null
pytest tests/test_resolver.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `pyproject.toml`**

```toml
# libs/synapto-remediator/pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "synapto-remediator"
version = "0.1.0"
description = "Workflow resolution and safety-gated execution engine for Synapto"
requires-python = ">=3.9"
dependencies = [
    "synapto-contracts",
    "pydantic>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["synapto_remediator*"]
```

- [ ] **Step 4: Create `models.py`**

```python
# libs/synapto-remediator/synapto_remediator/models.py
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ResolutionMethod(str, Enum):
    LIBRARY = "library"          # Exact match from catalogue
    SIMILARITY = "similarity"    # Semantic match from existing playbooks/SOPs
    AI = "ai"                    # AI synthesis fallback


class IncidentContext(BaseModel):
    incident_id: str
    title: str
    sanitized_title: str
    os_family: Optional[str] = None
    layer: Optional[str] = None
    tenant_id: Optional[str] = None
    meta_data: Dict[str, Any] = {}


class Resolution(BaseModel):
    playbook_id: Optional[str] = None
    playbook_name: Optional[str] = None
    playbook_steps: List[Dict[str, Any]] = []
    method: ResolutionMethod
    was_generated: bool
    source_sop_id: Optional[str] = None
```

- [ ] **Step 5: Create minimal `__init__.py`**

```python
# libs/synapto-remediator/synapto_remediator/__init__.py
from .models import IncidentContext, Resolution, ResolutionMethod
from .engine import RemediationEngine
```

Create a stub `engine.py` so the import works:

```python
# libs/synapto-remediator/synapto_remediator/engine.py
class RemediationEngine:
    pass
```

- [ ] **Step 6: Run tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-remediator
pip install -e ../synapto-contracts -e .
pytest tests/test_resolver.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 7: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-remediator/
git commit -m "feat(remediator): scaffold synapto-remediator with domain models"
```

---

### Task 7: Title sanitizer + RemediationEngine

**Files:**
- Create: `libs/synapto-remediator/synapto_remediator/sanitizer.py`
- Modify: `libs/synapto-remediator/synapto_remediator/engine.py`
- Create: `libs/synapto-remediator/tests/test_engine.py`

- [ ] **Step 1: Write failing test**

```python
# libs/synapto-remediator/tests/test_engine.py
from synapto_remediator.sanitizer import sanitize_title


def test_sanitize_removes_ip_addresses():
    result = sanitize_title("High CPU on 10.0.0.1")
    assert "10.0.0.1" not in result


def test_sanitize_removes_percentages():
    result = sanitize_title("CPU Usage > 90% on web-01")
    assert "90" not in result


def test_sanitize_removes_host_suffix():
    result = sanitize_title("disk full on db-master-01")
    assert "db-master-01" not in result


def test_sanitize_lowercases():
    result = sanitize_title("HIGH CPU USAGE")
    assert result == result.lower()


def test_sanitize_empty_string():
    assert sanitize_title("") == ""


def test_jaccard_similarity():
    from synapto_remediator.engine import jaccard_similarity
    assert jaccard_similarity("high cpu usage", "high cpu load") > 0.4
    assert jaccard_similarity("disk full cleanup", "completely unrelated") < 0.3
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-remediator
pytest tests/test_engine.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Implement `sanitizer.py`**

```python
# libs/synapto-remediator/synapto_remediator/sanitizer.py
import re


def sanitize_title(title: str) -> str:
    """Strip IPs, hostnames, numbers, and stopwords for generic matching."""
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '', t)   # IPv4
    t = re.sub(r'^sop:\s*', '', t)                         # SOP: prefix
    t = re.sub(r'\s+on\s+[\w\-\.]+', '', t, flags=re.IGNORECASE)  # "on <host>"
    t = re.sub(r'\d+%?', '', t)                            # numbers / percentages
    t = re.sub(r'\b(at|on|is|of|high|low|critical|warning)\b', '', t)
    t = re.sub(r'automated:\s*', '', t)                    # "Automated: " prefix
    t = re.sub(r'\s+', ' ', t).strip()
    return t.rstrip(' -:')
```

- [ ] **Step 4: Implement `jaccard_similarity` in `engine.py`**

```python
# libs/synapto-remediator/synapto_remediator/engine.py
from typing import Optional
from .models import IncidentContext, Resolution, ResolutionMethod
from .sanitizer import sanitize_title


def jaccard_similarity(a: str, b: str) -> float:
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(tokens_a & tokens_b) / len(union)


class RemediationEngine:
    """
    Stateless resolution helper.
    Caller provides candidate playbooks/SOPs; engine scores and selects best match.
    """
    PLAYBOOK_MATCH_THRESHOLD = 0.6
    SOP_MATCH_THRESHOLD = 0.5
    SOP_OS_BONUS = 0.15
    SOP_OS_PENALTY = -0.30

    def find_best_playbook(
        self,
        context: IncidentContext,
        playbooks: list[dict],
    ) -> Optional[Resolution]:
        """Pass 1 & 1.5: exact or semantic playbook match."""
        best_score = 0.0
        best_pb = None

        for pb in playbooks:
            pb_sanitized = sanitize_title(pb.get("name", ""))
            score = jaccard_similarity(context.sanitized_title, pb_sanitized)
            if score > best_score and score >= self.PLAYBOOK_MATCH_THRESHOLD:
                best_score = score
                best_pb = pb

        if best_pb:
            return Resolution(
                playbook_id=best_pb["id"],
                playbook_name=best_pb.get("name"),
                playbook_steps=best_pb.get("steps", []),
                method=ResolutionMethod.SIMILARITY,
                was_generated=False,
            )
        return None

    def find_best_sop(
        self,
        context: IncidentContext,
        sops: list[dict],
    ) -> Optional[dict]:
        """Pass 2: SOP library match with OS-family scoring."""
        best_score = 0.0
        best_sop = None

        for sop in sops:
            sop_sanitized = sanitize_title(sop.get("title", ""))
            title_score = jaccard_similarity(context.sanitized_title, sop_sanitized)

            sop_os = (sop.get("meta_data") or {}).get("os_family")
            if sop_os and context.os_family:
                os_bonus = self.SOP_OS_BONUS if sop_os.lower() == context.os_family.lower() else self.SOP_OS_PENALTY
            else:
                os_bonus = 0.0

            score = title_score + os_bonus
            if score > best_score and score >= self.SOP_MATCH_THRESHOLD:
                best_score = score
                best_sop = sop

        return best_sop
```

- [ ] **Step 5: Run all remediator tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-remediator
pytest tests/ -v
```

Expected: All 8 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-remediator/
git commit -m "feat(remediator): add title sanitizer and RemediationEngine matching logic"
```

---

### Task 8: Wire orchestration-layer to use synapto-remediator

**Files:**
- Modify: `backend/orchestration-layer/Dockerfile`
- Modify: `backend/orchestration-layer/main.py`

- [ ] **Step 1: Update Dockerfile**

Add to the lib install block:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-detector && \
    pip install --no-cache-dir /app/libs/synapto-classifier && \
    pip install --no-cache-dir /app/libs/synapto-remediator
```

- [ ] **Step 2: Import in main.py**

At the imports block in `backend/orchestration-layer/main.py`, add:

```python
from synapto_remediator import RemediationEngine, IncidentContext
from synapto_remediator.sanitizer import sanitize_title as _sanitize_title_for_matching
```

Remove the existing `_sanitize_title_for_matching` function definition (currently at lines ~553–579) — it is now provided by the library.

Replace the two scoring blocks inside `assign_playbook_to_incident` (playbook semantic match at lines ~627–658, and SOP match at lines ~660–698) with calls to the engine:

```python
# After the Knowledge Layer exact-match attempt (step 1), replace step 1.5 with:

_engine = RemediationEngine()
_ctx = IncidentContext(
    incident_id=incident_id,
    title=incident.title,
    sanitized_title=sanitized_title,
    os_family=os_family,
    layer=(incident.meta_data or {}).get("layer"),
    tenant_id=str(incident.tenant_id) if incident.tenant_id else None,
)

# Step 1.5: semantic playbook match
if not playbook_id:
    pb_res = await client.get(f"{KNOWLEDGE_LAYER_URL}/playbooks", timeout=10.0)
    if pb_res.status_code == 200:
        resolution = _engine.find_best_playbook(_ctx, pb_res.json())
        if resolution:
            incident.assigned_playbook_id = uuid.UUID(resolution.playbook_id)
            incident.status = IncidentStatus.INVESTIGATING
            db.commit()
            await execute_remediation(incident_id, db)
            return

# Step 2: SOP match
sops_res = await client.get(f"{KNOWLEDGE_LAYER_URL}/sops", timeout=10.0)
if sops_res.status_code == 200:
    matched_sop = _engine.find_best_sop(_ctx, sops_res.json())
    # ... rest of existing SOP logic unchanged ...
```

- [ ] **Step 3: Rebuild and verify**

```bash
cd /Users/alind/Projects/Synapto
docker compose build orchestration-layer 2>&1 | tail -5
docker compose up -d orchestration-layer
sleep 5
docker logs synapto-orchestration-layer-7 --tail=10
```

Expected: No ImportError, service starts.

- [ ] **Step 4: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add backend/orchestration-layer/ libs/synapto-remediator/
git commit -m "feat(orchestration): use synapto-remediator for playbook/SOP matching"
```

---

### Task 9: Complete AI-to-Catalogue promotion

The `promote_to_catalogue` endpoint at line ~1459 of `main.py` is a stub. It sets a flag but never calls the Knowledge Layer. Complete it by adding `is_gold_standard` to the Script model and wiring the promote endpoint.

**Files:**
- Modify: `backend/shared/models.py` — add `is_gold_standard` to Script
- Modify: `backend/knowledge-layer/main.py` — add `PATCH /scripts/{id}` endpoint
- Modify: `backend/orchestration-layer/main.py` — complete `promote_to_catalogue`

- [ ] **Step 1: Add `is_gold_standard` column to Script model**

In `backend/shared/models.py`, find the `Script` class and add the column:

```python
# Find the Script class in backend/shared/models.py and add:
is_gold_standard = Column(Boolean, default=False, nullable=False)
```

- [ ] **Step 2: Add PATCH endpoint to knowledge-layer**

In `backend/knowledge-layer/main.py`, add after the existing scripts endpoints:

```python
@app.patch("/scripts/{script_id}")
def update_script(
    script_id: str,
    updates: dict,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update script metadata (e.g., promote to gold standard)."""
    import uuid as _uuid
    script = db.query(Script).filter(Script.id == _uuid.UUID(script_id)).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    allowed_fields = {"is_gold_standard", "description", "category"}
    for field, value in updates.items():
        if field in allowed_fields and hasattr(script, field):
            setattr(script, field, value)

    db.commit()
    db.refresh(script)
    return {"id": str(script.id), "is_gold_standard": script.is_gold_standard}
```

- [ ] **Step 3: Complete `promote_to_catalogue` in orchestration-layer**

Replace the stub body of `promote_to_catalogue` in `backend/orchestration-layer/main.py`:

```python
@app.post("/incidents/{incident_id}/promote")
async def promote_to_catalogue(incident_id: str, db: Session = Depends(get_db)):
    """[ENTERPRISE] Promote a successful AI-fix to the permanent Action Catalogue."""
    import uuid
    incident = db.query(Incident).filter(Incident.id == uuid.UUID(incident_id)).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    meta = incident.meta_data or {}
    if not meta.get("promotion_eligible"):
        raise HTTPException(status_code=400, detail="Incident is not eligible for promotion")

    try:
        playbook = incident.playbook
        if not playbook:
            raise HTTPException(status_code=400, detail="No playbook attached to incident")

        # Find all composite scripts generated for this playbook
        async with httpx.AsyncClient() as client:
            scripts_res = await client.get(
                f"{KNOWLEDGE_LAYER_URL}/scripts",
                params={"meta_data_playbook_id": str(playbook.id), "tenant_id": str(incident.tenant_id)},
                headers=_service_headers(),
                timeout=10.0
            )
            scripts = scripts_res.json() if scripts_res.status_code == 200 else []

            promoted_count = 0
            for script in scripts:
                patch_res = await client.patch(
                    f"{KNOWLEDGE_LAYER_URL}/scripts/{script['id']}",
                    json={"is_gold_standard": True},
                    headers=_service_headers(),
                    timeout=10.0
                )
                if patch_res.status_code == 200:
                    promoted_count += 1
                    logger.info(f"[PROMOTION] Script {script['id']} promoted to gold standard.")

        new_meta = incident.meta_data.copy()
        new_meta["promotion_eligible"] = False
        new_meta["is_promoted"] = True
        new_meta["promoted_scripts"] = promoted_count
        incident.meta_data = new_meta
        db.commit()

        return {"success": True, "message": f"Promoted {promoted_count} script(s) to Action Catalogue."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Promotion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 4: Rebuild affected services**

```bash
cd /Users/alind/Projects/Synapto
docker compose build orchestration-layer knowledge-layer 2>&1 | tail -5
docker compose up -d orchestration-layer knowledge-layer
sleep 5
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "orchestration|knowledge"
```

Expected: Both services `Up`.

- [ ] **Step 5: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add backend/shared/models.py backend/knowledge-layer/main.py backend/orchestration-layer/main.py
git commit -m "feat(promotion): complete AI-to-Catalogue promotion — sets is_gold_standard on scripts"
```

---

## Track 3: `synapto-cicd` Library

### Task 10: Package scaffold + CICDRiskScorer

**Files:**
- Create: `libs/synapto-cicd/pyproject.toml`
- Create: `libs/synapto-cicd/synapto_cicd/__init__.py`
- Create: `libs/synapto-cicd/synapto_cicd/models.py`
- Create: `libs/synapto-cicd/synapto_cicd/scorer.py`
- Create: `libs/synapto-cicd/tests/__init__.py`
- Create: `libs/synapto-cicd/tests/test_scorer.py`

- [ ] **Step 1: Write the failing test**

```python
# libs/synapto-cicd/tests/test_scorer.py
import pytest
from synapto_cicd.models import CICDDeployment
from synapto_cicd.scorer import CICDRiskScorer


def _deployment(**kwargs) -> CICDDeployment:
    defaults = dict(
        service_name="api-service",
        changed_files=["src/api.py"],
        has_db_migration=False,
        is_off_hours=False,
        affected_services=[],
        environment="staging",
        rollback_available=True,
    )
    defaults.update(kwargs)
    return CICDDeployment(**defaults)


def test_simple_staging_deploy_is_low_risk():
    result = CICDRiskScorer().score(_deployment())
    assert result.risk_level in ("low", "medium")
    assert result.requires_manual_approval is False


def test_production_deploy_with_migration_is_high_risk():
    result = CICDRiskScorer().score(_deployment(
        environment="production",
        has_db_migration=True,
    ))
    assert result.risk_score > 0.6
    assert result.requires_manual_approval is True


def test_off_hours_production_deploy_increases_risk():
    staging = CICDRiskScorer().score(_deployment(environment="production", is_off_hours=False))
    offhours = CICDRiskScorer().score(_deployment(environment="production", is_off_hours=True))
    assert offhours.risk_score >= staging.risk_score


def test_many_changed_files_increases_risk():
    small = CICDRiskScorer().score(_deployment(changed_files=["a.py"]))
    large = CICDRiskScorer().score(_deployment(changed_files=[f"file{i}.py" for i in range(50)]))
    assert large.risk_score > small.risk_score


def test_no_rollback_increases_risk():
    with_rb = CICDRiskScorer().score(_deployment(rollback_available=True))
    without_rb = CICDRiskScorer().score(_deployment(rollback_available=False))
    assert without_rb.risk_score >= with_rb.risk_score


def test_risk_factors_list_explains_decision():
    result = CICDRiskScorer().score(_deployment(
        environment="production",
        has_db_migration=True,
        is_off_hours=True,
    ))
    assert len(result.risk_factors) >= 2


def test_risk_score_bounds():
    result = CICDRiskScorer().score(_deployment())
    assert 0.0 <= result.risk_score <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-cicd
pytest tests/test_scorer.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `pyproject.toml`**

```toml
# libs/synapto-cicd/pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "synapto-cicd"
version = "0.1.0"
description = "CI/CD deployment risk scoring for Synapto AIOps"
requires-python = ">=3.9"
dependencies = [
    "pydantic>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["synapto_cicd*"]
```

- [ ] **Step 4: Create `models.py`**

```python
# libs/synapto-cicd/synapto_cicd/models.py
from typing import List, Optional
from pydantic import BaseModel


class CICDDeployment(BaseModel):
    service_name: str
    changed_files: List[str]
    has_db_migration: bool
    is_off_hours: bool
    affected_services: List[str]
    environment: str        # "production", "staging", "development"
    rollback_available: bool
    commit_message: Optional[str] = None


class CICDRiskAssessment(BaseModel):
    risk_score: float       # 0.0–1.0
    risk_level: str         # "low", "medium", "high", "critical"
    risk_factors: List[str]
    requires_manual_approval: bool
    recommendation: str
```

- [ ] **Step 5: Implement `scorer.py`**

```python
# libs/synapto-cicd/synapto_cicd/scorer.py
from .models import CICDDeployment, CICDRiskAssessment


class CICDRiskScorer:
    """
    Scores a CI/CD deployment for risk.
    Returns a CICDRiskAssessment with risk_score 0.0–1.0.
    Factors: environment, DB migration, changed file count, off-hours, rollback availability.
    """
    APPROVAL_THRESHOLD = 0.6

    def score(self, deployment: CICDDeployment) -> CICDRiskAssessment:
        score = 0.0
        factors = []

        # Environment weight
        env_weights = {"production": 0.30, "staging": 0.10, "development": 0.0}
        env_score = env_weights.get(deployment.environment.lower(), 0.10)
        if env_score > 0:
            score += env_score
            if deployment.environment.lower() == "production":
                factors.append("Production environment deployment")

        # DB migration
        if deployment.has_db_migration:
            score += 0.30
            factors.append("Database migration included")

        # Changed file count
        file_count = len(deployment.changed_files)
        if file_count > 30:
            score += 0.20
            factors.append(f"Large changeset ({file_count} files)")
        elif file_count > 10:
            score += 0.10
            factors.append(f"Medium changeset ({file_count} files)")

        # Off-hours
        if deployment.is_off_hours:
            score += 0.15
            factors.append("Off-hours deployment")

        # No rollback
        if not deployment.rollback_available:
            score += 0.15
            factors.append("No rollback available")

        # Multiple affected services
        if len(deployment.affected_services) > 2:
            score += 0.10
            factors.append(f"Affects {len(deployment.affected_services)} services")

        score = round(min(score, 1.0), 3)
        requires_approval = score >= self.APPROVAL_THRESHOLD

        if score < 0.3:
            level, recommendation = "low", "Deploy with standard monitoring."
        elif score < 0.6:
            level, recommendation = "medium", "Deploy during business hours with enhanced monitoring."
        elif score < 0.8:
            level, recommendation = "high", "Requires manual approval and rollback plan."
        else:
            level, recommendation = "critical", "Requires senior engineer approval, staged rollout, and war room."

        return CICDRiskAssessment(
            risk_score=score,
            risk_level=level,
            risk_factors=factors,
            requires_manual_approval=requires_approval,
            recommendation=recommendation,
        )
```

- [ ] **Step 6: Create `__init__.py`**

```python
# libs/synapto-cicd/synapto_cicd/__init__.py
from .models import CICDDeployment, CICDRiskAssessment
from .scorer import CICDRiskScorer
```

- [ ] **Step 7: Run all tests**

```bash
cd /Users/alind/Projects/Synapto/libs/synapto-cicd
pip install -e .
pytest tests/test_scorer.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 8: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-cicd/
git commit -m "feat(cicd): add synapto-cicd with CICDRiskScorer"
```

---

### Task 11: Expose CI/CD risk scoring via integration-layer webhook

**Files:**
- Modify: `backend/integration-layer/Dockerfile`
- Create: `backend/integration-layer/routers/cicd.py`
- Modify: `backend/integration-layer/main.py`
- Modify: `backend/api-gateway/main.py`

- [ ] **Step 1: Add synapto-cicd to integration-layer Dockerfile**

In `backend/integration-layer/Dockerfile`, update the lib install block:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry && \
    pip install --no-cache-dir /app/libs/synapto-cicd
```

- [ ] **Step 2: Create the CI/CD router**

```python
# backend/integration-layer/routers/cicd.py
from fastapi import APIRouter
from synapto_cicd import CICDDeployment, CICDRiskScorer, CICDRiskAssessment

router = APIRouter(prefix="/cicd", tags=["cicd"])
_scorer = CICDRiskScorer()


@router.post("/risk-assessment", response_model=CICDRiskAssessment)
def assess_deployment_risk(deployment: CICDDeployment):
    """
    Score a CI/CD deployment for risk.
    Call this from your CI pipeline before deploying to production.
    Returns risk_score 0.0-1.0 and whether manual approval is required.
    """
    return _scorer.score(deployment)
```

- [ ] **Step 3: Register router in integration-layer main.py**

In `backend/integration-layer/main.py`, add after the existing router imports:

```python
from routers import events, webhooks, cicd as cicd_router
```

And after the existing `app.include_router` calls:

```python
app.include_router(cicd_router.router, prefix="/api/v1")
```

- [ ] **Step 4: Add API gateway proxy**

In `backend/api-gateway/main.py`, find the section that proxies to integration-layer and add:

```python
@app.post("/api/v1/cicd/risk-assessment")
async def cicd_risk_assessment(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Proxy CI/CD risk assessment to integration-layer."""
    body = await request.json()
    # INTEGRATION_URL is already defined in api-gateway/main.py as:
    # os.getenv("INTEGRATION_URL", "http://integration-layer:8001")
    integration_url = os.getenv("INTEGRATION_URL", "http://integration-layer:8001")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{integration_url}/api/v1/cicd/risk-assessment",
            json=body,
            timeout=10.0,
        )
        return JSONResponse(status_code=response.status_code, content=response.json())

- [ ] **Step 5: Rebuild and verify**

```bash
cd /Users/alind/Projects/Synapto
docker compose build integration-layer api-gateway 2>&1 | tail -5
docker compose up -d integration-layer api-gateway
sleep 5
curl -s -X POST http://localhost:8000/api/v1/cicd/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{"service_name":"test","changed_files":["a.py"],"has_db_migration":false,"is_off_hours":false,"affected_services":[],"environment":"staging","rollback_available":true}' \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:3000/api/v1/auth/token -d 'username=admin&password=admin' -H 'Content-Type: application/x-www-form-urlencoded' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')" | python3 -m json.tool
```

Expected: JSON response with `risk_score`, `risk_level`, `recommendation`.

- [ ] **Step 6: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add backend/integration-layer/ backend/api-gateway/main.py
git commit -m "feat(cicd): expose CI/CD risk assessment endpoint via integration-layer"
```

---

## Track 4: `synapto-sdk` Meta-package

### Task 12: Create synapto-sdk

**Files:**
- Create: `libs/synapto-sdk/pyproject.toml`
- Create: `libs/synapto-sdk/synapto_sdk/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
# libs/synapto-sdk/pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "synapto-sdk"
version = "0.1.0"
description = "Meta-package: installs the full Synapto AIOps library suite"
requires-python = ">=3.9"
dependencies = [
    "synapto-contracts",
    "synapto-telemetry",
    "synapto-detector",
    "synapto-classifier",
    "synapto-remediator",
    "synapto-cicd",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["synapto_sdk*"]
```

- [ ] **Step 2: Create `__init__.py`**

```python
# libs/synapto-sdk/synapto_sdk/__init__.py
"""
synapto-sdk — Meta-package for the Synapto AIOps Library Suite.

Installing this package pulls in all AIOps libraries:
  - synapto-contracts: shared Pydantic schemas
  - synapto-telemetry: OTel instrumentation
  - synapto-detector:  statistical anomaly detection
  - synapto-classifier: 6-pass incident classification
  - synapto-remediator: workflow resolution and safety gating
  - synapto-cicd:      CI/CD risk scoring
"""
from synapto_contracts import (
    AnomalySignal, IncidentClassification, RemediationSafety,
    Workflow, WorkflowResult, TelemetrySignal,
)
from synapto_telemetry import TelemetryEmitter
from synapto_detector import DetectionEngine
from synapto_classifier import ClassifierPipeline
from synapto_remediator import RemediationEngine
from synapto_cicd import CICDRiskScorer

__all__ = [
    "AnomalySignal", "IncidentClassification", "RemediationSafety",
    "Workflow", "WorkflowResult", "TelemetrySignal",
    "TelemetryEmitter", "DetectionEngine", "ClassifierPipeline",
    "RemediationEngine", "CICDRiskScorer",
]
```

- [ ] **Step 3: Verify install**

```bash
cd /Users/alind/Projects/Synapto
pip install -e libs/synapto-contracts -e libs/synapto-telemetry -e libs/synapto-detector \
    -e libs/synapto-classifier -e libs/synapto-remediator -e libs/synapto-cicd \
    -e libs/synapto-sdk
python -c "from synapto_sdk import ClassifierPipeline, CICDRiskScorer; print('SDK OK')"
```

Expected: `SDK OK`

- [ ] **Step 4: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add libs/synapto-sdk/
git commit -m "feat(sdk): add synapto-sdk meta-package"
```

---

## Track 5: Service Instrumentation

All 7 tasks follow the same pattern:
1. Add `synapto-telemetry` to Dockerfile
2. Add `instrument_app(app, service_name="...", redis_client=redis_client)` after app creation in `main.py`
3. Rebuild and verify no crash

The sync `redis_client` from `shared.redis_utils` is already available in all services (they share the same `shared/` module and `.env`). Import it as `from shared.redis_utils import redis_client`.

---

### Task 13: Instrument execution-engine

**Files:**
- Modify: `backend/execution-engine/Dockerfile`
- Modify: `backend/execution-engine/main.py`

- [ ] **Step 1: Update Dockerfile**

In `backend/execution-engine/Dockerfile`, find:
```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts
```
Replace with:
```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

In `backend/execution-engine/main.py`, add at the imports section:

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After the `app = FastAPI(...)` block, add:

```python
instrument_app(app, service_name="execution-engine", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
cd /Users/alind/Projects/Synapto
docker compose build execution-engine 2>&1 | tail -3
docker compose up -d execution-engine
sleep 4
docker logs synapto-execution --tail=5 2>&1
```

Expected: Logs show service started, no ImportError.

- [ ] **Step 4: Commit**

```bash
cd /Users/alind/Projects/Synapto
git add backend/execution-engine/
git commit -m "feat(telemetry): instrument execution-engine"
```

---

### Task 14: Instrument knowledge-layer

**Files:**
- Modify: `backend/knowledge-layer/Dockerfile`
- Modify: `backend/knowledge-layer/main.py`

- [ ] **Step 1: Update Dockerfile**

In `backend/knowledge-layer/Dockerfile`, find the lib install block and add `synapto-telemetry`:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

In `backend/knowledge-layer/main.py`, add after existing imports:

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(...)`:

```python
instrument_app(app, service_name="knowledge-layer", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build knowledge-layer 2>&1 | tail -3
docker compose up -d knowledge-layer
sleep 4
docker logs synapto-knowledge --tail=5 2>&1
```

Expected: Clean startup.

- [ ] **Step 4: Commit**

```bash
git add backend/knowledge-layer/
git commit -m "feat(telemetry): instrument knowledge-layer"
```

---

### Task 15: Instrument learning-engine

**Files:**
- Modify: `backend/learning-engine/Dockerfile`
- Modify: `backend/learning-engine/main.py`

- [ ] **Step 1: Update Dockerfile** — same pattern:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(...)`:

```python
instrument_app(app, service_name="learning-engine", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build learning-engine 2>&1 | tail -3
docker compose up -d learning-engine
sleep 4
docker logs synapto-learning --tail=5 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add backend/learning-engine/
git commit -m "feat(telemetry): instrument learning-engine"
```

---

### Task 16: Instrument api-gateway

**Files:**
- Modify: `backend/api-gateway/Dockerfile`
- Modify: `backend/api-gateway/main.py`

- [ ] **Step 1: Update Dockerfile**

In `backend/api-gateway/Dockerfile`, add `synapto-telemetry` to the lib install:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

The api-gateway already imports `event_stream` from `shared.redis_utils`. Use its `client`:

```python
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(...)`:

```python
instrument_app(app, service_name="api-gateway", redis_client=event_stream.client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build api-gateway 2>&1 | tail -3
docker compose up -d api-gateway
sleep 4
docker logs synapto-gateway --tail=5 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add backend/api-gateway/
git commit -m "feat(telemetry): instrument api-gateway"
```

---

### Task 17: Instrument auth-service

**Files:**
- Modify: `backend/auth-service/Dockerfile`
- Modify: `backend/auth-service/main.py`

- [ ] **Step 1: Update Dockerfile** — add `synapto-telemetry`:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(...)`:

```python
instrument_app(app, service_name="auth-service", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build auth-service 2>&1 | tail -3
docker compose up -d auth-service
sleep 5
docker logs synapto-auth --tail=5 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add backend/auth-service/
git commit -m "feat(telemetry): instrument auth-service"
```

---

### Task 18: Instrument admin-service

**Files:**
- Modify: `backend/admin-service/Dockerfile`
- Modify: `backend/admin-service/main.py`

- [ ] **Step 1: Update Dockerfile** — add `synapto-telemetry`:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(title="Admin Service", version="1.0.0")`:

```python
instrument_app(app, service_name="admin-service", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build admin-service 2>&1 | tail -3
docker compose up -d admin-service
sleep 4
docker logs synapto-admin --tail=5 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add backend/admin-service/
git commit -m "feat(telemetry): instrument admin-service"
```

---

### Task 19: Instrument itsm-connector

**Files:**
- Modify: `backend/itsm-connector/Dockerfile`
- Modify: `backend/itsm-connector/main.py`

- [ ] **Step 1: Update Dockerfile** — add `synapto-telemetry`:

```dockerfile
RUN pip install --no-cache-dir /app/libs/synapto-contracts && \
    pip install --no-cache-dir /app/libs/synapto-telemetry
```

- [ ] **Step 2: Instrument in main.py**

```python
from shared.redis_utils import redis_client
from synapto_telemetry.fastapi import instrument_app
```

After `app = FastAPI(...)`:

```python
instrument_app(app, service_name="itsm-connector", redis_client=redis_client)
```

- [ ] **Step 3: Rebuild and verify**

```bash
docker compose build itsm-connector 2>&1 | tail -3
docker compose up -d itsm-connector
sleep 4
docker logs synapto-itsm --tail=5 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add backend/itsm-connector/
git commit -m "feat(telemetry): instrument itsm-connector — all 8 services now telemetered"
```

---

## Final Verification

After completing all tracks, verify the full stack:

```bash
cd /Users/alind/Projects/Synapto
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected: All containers show `Up`, none showing `Restarting`.

```bash
# Verify telemetry stream is populated
docker exec synapto-redis redis-cli -a "${REDIS_PASSWORD:-changeme-redis-password}" XLEN synapto:telemetry
```

Expected: A non-zero count (spans flowing from instrumented services).

```bash
# Verify classifier library
docker exec synapto-orchestration-layer-7 python -c "from synapto_classifier import ClassifierPipeline; print('classifier OK')"

# Verify cicd endpoint
curl -s http://localhost:8000/api/v1/cicd/risk-assessment \
  -X POST -H "Content-Type: application/json" \
  -d '{"service_name":"test","changed_files":["a.py"],"has_db_migration":false,"is_off_hours":false,"affected_services":[],"environment":"staging","rollback_available":true}' | python3 -m json.tool
```

```bash
git tag v0.2.0-aiops-complete
```

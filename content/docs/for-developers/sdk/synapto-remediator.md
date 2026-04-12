# synapto-remediator

Workflow resolution engine with safety gating. Validates that a proposed remediation is safe to run before the Execution Engine executes it.

## Install

```bash
pip install -e libs/synapto-remediator
```

## Usage

```python
from synapto_remediator import RemediationEngine
from synapto_contracts import Workflow

engine = RemediationEngine()
workflow = Workflow(
    incident_id="abc123",
    steps=[{"category": "remediation", "script": "systemctl restart nginx"}],
    target_host="web-01",
)
result = engine.resolve(workflow)
print(result.safe)    # True / False
print(result.reason)  # If False: reason why it was blocked
```

## Safety gating

The engine checks:
- Script does not contain known destructive patterns (e.g. `rm -rf /`, `DROP TABLE`)
- Target host is in the known topology
- Policy mode allows remediation (not `DIAGNOSTIC_ONLY`)

If any check fails, `result.safe = False` and the workflow is not submitted to the Execution Engine.

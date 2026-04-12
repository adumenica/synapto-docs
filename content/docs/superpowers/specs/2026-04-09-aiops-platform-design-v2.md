# AIOps Platform — Library-First Architecture Design (v2)

**Date:** 2026-04-09
**Status:** Under Review
**Author:** Principal Software Architect
**Codebase:** Synapto — Self-Healing Infrastructure Platform

---

## 1. Context & Goals

Synapto is evolving from a reactive remediation platform into a proactive AIOps ecosystem. This design outlines the transition to a **Library-First** model where intelligence and automation are embedded directly into services via independent SDKs.

### Core Objectives:
1. **Instrument Everything**: Uniform telemetry across all microservices and agents.
2. **Hybrid Detection**: Move from fixed thresholds to statistical + ML baselining.
3. **Safety-First Automation**: Replace brittle playbooks with flexible Workflows governed by explicit **Safety Gates**.

### The Core Constraint: Library-First
All capabilities are built as Python libraries under `libs/`. No new microservices. The remediation philosophy is strictly:
**Library Match (Catalogue) → ML Similarity Match (Historical) → AI Synthesis (Fallback) → Human-in-the-Loop (Safety).**

---

## 2. Updated Repository Structure

```
Synapto/
├── backend/                    # Core microservices
├── libs/                       # AIOps library monorepo
│   ├── synapto-contracts/      # Shared Pydantic schemas (Zero Logic)
│   ├── synapto-telemetry/      # OTel instrumentation & exporters
│   ├── synapto-detector/       # Statistical & ML anomaly detection
│   ├── synapto-classifier/     # Noise filter & Incident classification
│   ├── synapto-remediator/     # Workflow engine & Safety Gates [UPDATED]
│   ├── synapto-cicd/           # CI/CD Risk scoring
│   └── synapto-sdk/            # Meta-package
```

---

## 3. `synapto-contracts` — The Safety Layer

We introduce explicit safety metadata to the core contracts to ensure that every remediation attempt is assessed for risk.

```python
# synapto-contracts/incident.py

class RemediationSafety(BaseModel):
    is_safe_to_auto_run: bool
    requires_approval: bool
    risk_score: float             # 0.0 (Safe) to 1.0 (Critical)
    risk_summary: str             # e.g., "AI-generated script contains destructive commands"
    approval_reason: Optional[str] # Why was this stopped for a human?

class IncidentClassification(BaseModel):
    incident_id: UUID
    layer: InfraLayer
    confidence: float
    method: Literal["rules", "ml", "ai"]
    is_duplicate: bool
    noise_score: float
    safety: RemediationSafety      # NEW: Safety assessment provided by classifier
    suggested_workflow_id: Optional[UUID]
```

---

## 4. `synapto-classifier` — Six-Pass Pipeline

The classifier now includes a final **Safety Validation** pass to decide if an incident should be auto-remediated or escalated to a human.

```
AnomalySignal
     │
     ▼
 [Pass 1] Noise Filter ──── noise_score > 0.75 ──► DISCARD
     │
 [Pass 2] Deduplicator ──── is_duplicate=True ──► SUPPRESS (Link)
     │
 [Pass 3] Rule Engine  ──── confidence >= 0.8 ──► CLASSIFY (Method: Rules)
     │
 [Pass 4] ML Classifier ── confidence >= 0.65 ──► CLASSIFY (Method: ML)
     │
 [Pass 5] AI Synthesis  ────────────────────────► CLASSIFY (Method: AI)
     │
     ▼
 [Pass 6] SAFETY GATE (New) ────────────────────► FINAL VERDICT
                                                  (Auto-Run vs. Human Approval)
```

### Safety Gate Logic:
- **Rules Match**: If a "Library Action" from the catalogue matches, `requires_approval` defaults to `False`.
- **AI Synthesis**: If Pass 5 was used, the classifier scans the generated script for destructive keywords (`rm`, `kill -9`, `drop table`). If found, it forces `requires_approval = True`.
- **Low Confidence**: If `confidence < 0.7`, it forces `requires_approval = True`.

---

## 5. `synapto-remediator` — Human-in-the-Loop & Fallback

The Remediator is the engine that executes the final verdict. It handles the "Unknown-Unknown" scenarios safely.

### The Emergency Break (Human Fallback)
If the system hits a "Dead End" (No library match and AI cannot generate a confident fix), it triggers the **Assisted Manual Remediation** flow:

1. **Incident Promotion**: The incident is created with a `status=unremediable`.
2. **Diagnostic Brief**: The `Learning Engine` generates a summary of existing symptoms and suggests human diagnostic steps.
3. **ITSM/Slack Routing**: A critical alert is sent to the on-call engineer with a "Remediation Workspace" link.

### Workflow Resolution Chain [REVISED]:

1. **Exact Match (Library)**: Use pre-approved catalogue actions.
2. **Similarity Match (ML)**: Use a previously successful human-validated workflow.
3. **Synthesis (AI)**: Generate a new workflow.
4. **Validation (Safety Gate)**: Check if synthesis is safe.
5. **Execution**: 
   - If **Safe**: Execute automatically in sandbox.
   - If **Unsafe**: Send "Interactive Approval" request to Operator.
   - If **Failed/Unknown**: Escalate to Human with Diagnostic Brief.

### Interactive Approval Request:
The operator sees a side-by-side view in the Synapto UI:
- **Trigger**: "High Disk Usage on DB-Master-01"
- **System Proposal**: "I found no known script. I generated a new 3-step cleanup script focusing on `/var/log`."
- **Risk Alert**: "Contains `rm -rf`. Human approval required."
- **Options**: [Run Now] [Modify Script] [Reject & Assign to Me]

---

## 6. Implementation Roadmap

### Step 1: Foundational SDKs (Weeks 1-2)
- Build `synapto-contracts` with Safety models.
- Refactor `backend/shared` to use the new contracts.

### Step 2: Edge Instrumentation (Weeks 3-4)
- Deploy `synapto-telemetry` to all microservices and the `synapto-agent`.
- Establish OTel traces for the full remediation loop.

### Step 3: Intelligence & Safety Gates (Weeks 5-8)
- Build `synapto-detector` (Statistical/ML).
- Build `synapto-classifier` with the **6-Pass Pipeline**.
- Implement the "Approval UI" in the React frontend.

### Step 4: Completion & Learning (Weeks 9-12)
- Roll out `synapto-remediator`.
- Activate "AI-to-Catalogue" promotion—successful human approvals are saved as new Library Actions.

---

## 7. Risk Mitigation

### ⚠️ Critical Risk: Blind Execution
The safety gates in `synapto-remediator` are mandatory. AI synthesis MUST NEVER execute without a high confidence score AND a "Safe" keyword scan result.

### 💡 Performance Tip: Warm Starts
Use the "Action Catalogue" as the primary source of truth. The system should always try to compose existing, tested actions into a workflow before asking the AI to write a raw script from scratch.

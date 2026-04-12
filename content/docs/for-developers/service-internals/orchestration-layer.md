# Orchestration Layer

**File:** `backend/orchestration-layer/main.py`  
**Port:** 8002

The Orchestration Layer is the "brain" — it consumes events, correlates them into incidents, decides what to do, and drives the full remediation lifecycle.

## Event consumption

A background `asyncio` task runs an infinite loop reading from the `events` Redis Stream using consumer group `orchestration-group`. Multiple instances can run in parallel — each event is processed by exactly one instance.

## Event → Incident

For each event consumed:

1. Check if an open incident already exists for the same host/type (deduplication).
2. Create a new `Incident` record with `status=open`.
3. Enrich metadata: look up hostname in `network_topology` for `os_family`, detect infrastructure layer, extract component name from labels.

## Three-Tier Playbook Matching

```
Tier 1 — Exact Playbook Match
  POST /playbooks/match to Knowledge Layer
  → Finds a configured policy for this incident type
  → If found: use the mapped playbook directly

Tier 2 — SOP Library Match (Jaccard similarity)
  → Sanitize incident title (strip IPs, percentages, hostnames)
  → Compare sanitized tokens against all SOP titles
  → If overlap score > 0.5: use the SOP to build a diagnostic playbook

Tier 3 — AI Diagnostic Generation (fallback)
  → If Tier 1 and 2 both miss: call Learning Engine
  → AI generates a new SOP + diagnostic playbook
  → Both are saved to the library (Tier 1/2 benefit next time)
```

## Composite script generation

Rather than executing playbook steps one by one, the Orchestration Layer groups steps by category and requests the Learning Engine to merge them into a single script per category. This reduces SSH connection overhead and makes execution atomic.

## Incident state machine

`open` → `investigating` → `remediating` → `resolved` → `closed`

## Policy enforcement

Policies can override execution mode:

| Mode | Behaviour |
|------|-----------|
| `STANDARD` | Run all playbook steps |
| `DIAGNOSTIC_ONLY` | Run diagnostic steps only |
| `APPROVAL_REQUIRED` | Block execution until an operator approves |

## Dead-letter handling

Failed events (after retries) are moved to the `events:dead-letter` Redis Stream for inspection.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `KNOWLEDGE_SERVICE_URL` | Knowledge Layer URL |
| `EXECUTION_SERVICE_URL` | Execution Engine URL |
| `LEARNING_SERVICE_URL` | Learning Engine URL |

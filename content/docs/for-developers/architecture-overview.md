# Architecture Overview

## What is Synapto?

Synapto is an **AI-augmented, self-healing infrastructure platform**. When a monitoring tool fires an alert, Synapto automatically:

1. Ingests and normalises the alert into an internal "Event"
2. Correlates related events into an "Incident"
3. Finds a matching remediation playbook (or generates one with AI)
4. Executes the remediation scripts on the affected infrastructure
5. Records everything and learns from the outcome

**Core philosophy — "Library-First, AI-Fallback":** Synapto always tries to resolve an incident using a pre-approved, human-validated SOP script first. AI only steps in when no match is found, and successful AI-generated fixes are automatically promoted into the SOP library for future reuse.

---

## Service Map

```
                      ┌───────────────────────────────┐
                      │       External World          │
                      │  Prometheus / CloudWatch /    │
                      │  Webhooks / Managed Hosts     │
                      └────────────┬──────────────────┘
                                   │ alerts / webhooks
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   selfhealing-network (Docker bridge)            │
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │  Frontend   │    │   API Gateway    │    │  Auth Service │  │
│  │  React SPA  │───▶│  Port 8000       │───▶│  Port 8006    │  │
│  │  Port 3000  │    │  (entry point,   │    │  (JWT, OAuth) │  │
│  └─────────────┘    │   auth, routing) │    └───────────────┘  │
│                     └────────┬─────────┘                        │
│                              │ routes to:                        │
│           ┌──────────────────┼──────────────────────┐          │
│           ▼                  ▼                       ▼          │
│  ┌────────────────┐ ┌────────────────┐  ┌────────────────────┐ │
│  │  Integration   │ │  Knowledge     │  │   Admin Service    │ │
│  │  Layer 8001    │ │  Layer 8003    │  │   Port 8007        │ │
│  │  (event ingest)│ │  (policies,    │  │  (users, settings) │ │
│  └───────┬────────┘ │   playbooks,   │  └────────────────────┘ │
│          │ publish  │   scripts, SOPs│                          │
│          ▼          └────────┬───────┘                          │
│   ┌────────────┐             │ query/match                      │
│   │Redis Stream│             ▼                                   │
│   │ "events"   │  ┌─────────────────┐    ┌───────────────────┐│
│   └─────┬──────┘  │  Orchestration  │───▶│  Execution Engine ││
│         │ consume │  Layer 8002     │    │  Port 8004        ││
│         └────────▶│  (correlation,  │    │  (SSH/WinRM/SQL/  ││
│                   │   policy match, │    │   Docker sandbox) ││
│                   │   workflow mgmt)│    └─────────┬─────────┘│
│                   └────────┬────────┘              │ or gRPC  │
│                            │ AI fallback            ▼          │
│                   ┌────────▼────────┐    ┌───────────────────┐│
│                   │ Learning Engine │    │  Agent Service    ││
│                   │  Port 8005      │    │  Port 50051 (gRPC)││
│                   │  (Claude/GPT,   │    │  (managed nodes)  ││
│                   │   SOP generation│    └───────────────────┘│
│                   └─────────────────┘                          │
│                                                                  │
│  ┌─────────────────────────┐  ┌────────────────────────────┐  │
│  │  PostgreSQL (port 5432) │  │  Redis (port 6379)         │  │
│  │  Primary database       │  │  Event stream + cache      │  │
│  └─────────────────────────┘  └────────────────────────────┘  │
│  ┌─────────────────────────┐                                    │
│  │  ITSM Connector 8008    │  (optional)                        │
│  └─────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

Only ports 3000 (Frontend) and 8000 (API Gateway) are exposed to the host. All other services communicate inside the Docker bridge network.

## Service Quick Reference

| Service | Container | Port | Role |
|---------|-----------|------|------|
| API Gateway | `selfhealing-gateway` | 8000 | Single public entry point; routes requests, enforces auth |
| Integration Layer | `selfhealing-integration` | 8001 | Ingests alerts; publishes to Redis Stream |
| Orchestration Layer | `selfhealing-orchestration` | 8002 | Correlates events → incidents; matches playbooks; drives remediation |
| Knowledge Layer | `selfhealing-knowledge` | 8003 | CRUD store for policies, playbooks, scripts, SOPs, topology |
| Execution Engine | `selfhealing-execution` | 8004 | Runs scripts via SSH / WinRM / Netmiko / Docker sandbox |
| Learning Engine | `selfhealing-learning` | 8005 | AI diagnostics (Claude/GPT), SOP generation, analytics |
| Auth Service | `selfhealing-auth` | 8006 | Login, JWT issuance, refresh, logout |
| Admin Service | `selfhealing-admin` | 8007 | User management, credentials vault, AI/ITSM settings |
| ITSM Connector | `selfhealing-itsm` | 8008 | Creates/updates tickets in ServiceNow, Jira, BMC (optional) |
| Agent Service | `selfhealing-agent` | 50051 | gRPC bridge for remote agents on managed nodes (mTLS) |
| PostgreSQL | `selfhealing-postgres` | 5432 | Primary relational database |
| Redis | `selfhealing-redis` | 6379 | Event stream (`events` channel) + distributed cache |
| Frontend | `selfhealing-frontend` | 3000 | React SPA served by Nginx |

---

## End-to-End Data Flow

This walkthrough traces a complete alert from ingestion to resolution.

**Scenario:** Prometheus fires a `high_cpu` alert for `web-server-01`.

```
Step 1 — Alert Arrives
  POST http://<server>:8000/api/v1/events
    { "source": "prometheus", "event_type": "high_cpu",
      "severity": "critical", "title": "CPU above 90% on web-server-01",
      "hostname": "web-server-01" }

Step 2 — API Gateway
  Receives on port 8000 (this endpoint is public — no auth)
  Forwards to: POST http://integration-layer:8001/api/v1/events

Step 3 — Integration Layer
  Parses Prometheus format → creates Event in PostgreSQL
  Publishes event_id to Redis Stream "events"
  Returns 201 { "event_id": "<uuid>" }

Step 4 — Orchestration Layer (background consumer)
  Reads "events" Redis Stream via consumer group "orchestration-group"
  Deduplication check: no open incident for web-server-01 + high_cpu
  Creates Incident { status="open", severity="critical" }
  Enriches: topology lookup → os_family="linux", layer="OS & Hardware"
  Triggers background remediation

Step 5 — Three-Tier Playbook Matching
  Tier 1: POST /playbooks/match → no exact match
  Tier 2: Jaccard similarity → "High CPU Usage Remediation" SOP (score 0.65)
           → generate diagnostic playbook from SOP steps
  Tier 3: (skipped — Tier 2 matched)

Step 6 — Execution
  POST http://execution-engine:8004/execute
    { script_content: "...", language: "bash", target_host: "web-server-01" }
  Execution Engine resolves SSH credentials from vault
  Opens SSH → runs script → captures stdout/stderr/exit_code
  Writes to executions table: { status="success", exit_code=0 }

Step 7 — Resolution
  Orchestration polls execution status (every 5s, max 5 min)
  Success → Incident.status = "resolved"
  If ITSM configured → closes external ticket
```

---

## Key Design Decisions

**Why Redis Streams (not a message queue)?** Streams support consumer groups (one event processed by exactly one consumer instance), message replay on restart, and persistent storage with configurable retention — all without a separate broker.

**Why JWT in HttpOnly cookies (not Authorization headers)?** HttpOnly cookies are inaccessible to JavaScript, eliminating XSS-based token theft. The trade-off is that CSRF protection must be explicit (handled by the SameSite cookie attribute and the origin check in the API Gateway).

**Why centralised auth in the API Gateway?** All backend microservices trust requests forwarded by the Gateway. This keeps JWT validation in one place and avoids duplicating auth logic in every service.

**Why the three-tier playbook matching?** Tier 1 (exact) is fast and deterministic. Tier 2 (similarity) handles variations in alert titles without requiring an exact configured mapping. Tier 3 (AI) handles genuinely novel incidents. Cost increases with tier — AI is only invoked when necessary.

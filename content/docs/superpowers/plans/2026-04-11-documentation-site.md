# Documentation Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a MkDocs Material documentation site with audience-first navigation covering all Synapto features through the latest sprint.

**Architecture:** Audience-first nav (For Operators / For Developers / Reference) using MkDocs Material with `navigation.tabs`. Content migrated from `docs/architecture/system_design.md` and `docs/manual/platform_how_to.md` into focused per-topic pages, plus new pages for CI/CD Risk, Action Catalogue, Service Health, SSE incidents, Agent Service, and the synapto-sdk suite.

**Tech Stack:** MkDocs 1.6+, mkdocs-material 9.x, mkdocs-git-revision-date-localized-plugin, pymdown-extensions. All content is Markdown. No build pipeline beyond `mkdocs build`.

---

## Scope Check

31 pages across 4 sections. All pages are content (no code changes to the application). The scope is large but every task is independent — a page can be written and the site rebuilt to verify at any point. No subsystem decomposition needed.

---

## File Map

**Create:**
```
mkdocs.yml                                            # MkDocs configuration
requirements-docs.txt                                 # pip deps for building the site
docs/index.md                                         # Home page

docs/for-operators/getting-started.md
docs/for-operators/default-credentials.md
docs/for-operators/webhook-integrations.md
docs/for-operators/incident-management.md
docs/for-operators/action-catalogue.md
docs/for-operators/cicd-risk.md
docs/for-operators/service-health.md
docs/for-operators/playbooks-and-policies.md
docs/for-operators/credential-vault.md
docs/for-operators/ai-configuration.md
docs/for-operators/itsm-integration.md
docs/for-operators/sso-configuration.md

docs/for-developers/getting-started.md
docs/for-developers/architecture-overview.md
docs/for-developers/service-internals/api-gateway.md
docs/for-developers/service-internals/integration-layer.md
docs/for-developers/service-internals/orchestration-layer.md
docs/for-developers/service-internals/knowledge-layer.md
docs/for-developers/service-internals/execution-engine.md
docs/for-developers/service-internals/learning-engine.md
docs/for-developers/service-internals/auth-service.md
docs/for-developers/service-internals/admin-service.md
docs/for-developers/service-internals/agent-service.md
docs/for-developers/service-internals/itsm-connector.md

docs/for-developers/sdk/overview.md
docs/for-developers/sdk/synapto-cicd.md
docs/for-developers/sdk/synapto-classifier.md
docs/for-developers/sdk/synapto-detector.md
docs/for-developers/sdk/synapto-remediator.md
docs/for-developers/sdk/synapto-telemetry.md

docs/for-developers/database-schema.md
docs/for-developers/adding-a-service.md
docs/for-developers/contracts.md

docs/reference/api.md
docs/reference/configuration.md
docs/reference/changelog.md
```

**Not modified:** existing files under `docs/architecture/`, `docs/manual/`, `docs/superpowers/`. They stay in place and are removed in Task 12 only after a clean build is confirmed.

---

## Task 1: MkDocs Scaffold

**Files:**
- Create: `mkdocs.yml`
- Create: `requirements-docs.txt`
- Create: `docs/index.md`

- [ ] **Step 1.1: Install MkDocs dependencies**

```bash
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin pymdown-extensions
```

Expected: installs without errors.

- [ ] **Step 1.2: Create `requirements-docs.txt`**

```
mkdocs>=1.6.0
mkdocs-material>=9.5.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
pymdown-extensions>=10.0
```

- [ ] **Step 1.3: Create `mkdocs.yml` at the repo root**

```yaml
site_name: Synapto Docs
site_description: Architecture and operator reference for the Synapto self-healing infrastructure platform
site_url: ""
docs_dir: docs
exclude_docs: |
  superpowers/
  architecture/
  manual/
  frontend-improvement-plan.md

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - toc.integrate
    - content.code.copy
    - content.code.annotate
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
  font:
    text: Inter
    code: JetBrains Mono

plugins:
  - search
  - tags
  - git-revision-date-localized:
      enable_creation_date: true

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - tables
  - toc:
      permalink: true
  - attr_list

nav:
  - Home: index.md
  - For Operators:
      - Getting Started: for-operators/getting-started.md
      - Default Credentials: for-operators/default-credentials.md
      - Webhook Integrations: for-operators/webhook-integrations.md
      - Incident Management: for-operators/incident-management.md
      - Action Catalogue: for-operators/action-catalogue.md
      - CI/CD Risk Assessment: for-operators/cicd-risk.md
      - Service Health: for-operators/service-health.md
      - Playbooks & Policies: for-operators/playbooks-and-policies.md
      - Credential Vault: for-operators/credential-vault.md
      - AI Configuration: for-operators/ai-configuration.md
      - ITSM Integration: for-operators/itsm-integration.md
      - SSO Configuration: for-operators/sso-configuration.md
  - For Developers:
      - Getting Started: for-developers/getting-started.md
      - Architecture Overview: for-developers/architecture-overview.md
      - Service Internals:
          - API Gateway: for-developers/service-internals/api-gateway.md
          - Integration Layer: for-developers/service-internals/integration-layer.md
          - Orchestration Layer: for-developers/service-internals/orchestration-layer.md
          - Knowledge Layer: for-developers/service-internals/knowledge-layer.md
          - Execution Engine: for-developers/service-internals/execution-engine.md
          - Learning Engine: for-developers/service-internals/learning-engine.md
          - Auth Service: for-developers/service-internals/auth-service.md
          - Admin Service: for-developers/service-internals/admin-service.md
          - Agent Service: for-developers/service-internals/agent-service.md
          - ITSM Connector: for-developers/service-internals/itsm-connector.md
      - SDK:
          - Overview: for-developers/sdk/overview.md
          - synapto-cicd: for-developers/sdk/synapto-cicd.md
          - synapto-classifier: for-developers/sdk/synapto-classifier.md
          - synapto-detector: for-developers/sdk/synapto-detector.md
          - synapto-remediator: for-developers/sdk/synapto-remediator.md
          - synapto-telemetry: for-developers/sdk/synapto-telemetry.md
      - Database Schema: for-developers/database-schema.md
      - Adding a Service: for-developers/adding-a-service.md
      - Contracts: for-developers/contracts.md
  - Reference:
      - API Reference: reference/api.md
      - Configuration: reference/configuration.md
      - Changelog: reference/changelog.md
```

- [ ] **Step 1.4: Create `docs/index.md`**

```markdown
# Synapto

**Synapto** is an AI-augmented, self-healing infrastructure platform. When a monitoring tool fires an alert, Synapto automatically ingests it, correlates related events into an incident, finds or generates a remediation playbook, executes the fix on the affected infrastructure, and learns from the outcome.

## Core philosophy — "Library-First, AI-Fallback"

Synapto always tries to resolve an incident using a pre-approved, human-validated SOP script first. AI only steps in when no match exists. Successful AI-generated fixes are automatically promoted into the SOP library for future reuse.

## Where to start

<div class="grid cards" markdown>

-   **For Operators**

    Deploy Synapto, configure integrations, and manage incidents from the UI.

    [Getting Started →](for-operators/getting-started.md)

-   **For Developers**

    Understand the internals, extend services, and use the Python SDK.

    [Architecture Overview →](for-developers/architecture-overview.md)

-   **API Reference**

    Endpoint summary and link to the interactive Swagger UI.

    [Reference →](reference/api.md)

-   **Configuration**

    All environment variables and Docker Compose overrides.

    [Configuration →](reference/configuration.md)

</div>
```

- [ ] **Step 1.5: Create placeholder files for all pages listed in the nav so the build doesn't fail**

Run this script from the repo root:

```bash
mkdir -p docs/for-operators docs/for-developers/service-internals docs/for-developers/sdk docs/reference

for f in \
  docs/for-operators/getting-started.md \
  docs/for-operators/default-credentials.md \
  docs/for-operators/webhook-integrations.md \
  docs/for-operators/incident-management.md \
  docs/for-operators/action-catalogue.md \
  docs/for-operators/cicd-risk.md \
  docs/for-operators/service-health.md \
  docs/for-operators/playbooks-and-policies.md \
  docs/for-operators/credential-vault.md \
  docs/for-operators/ai-configuration.md \
  docs/for-operators/itsm-integration.md \
  docs/for-operators/sso-configuration.md \
  docs/for-developers/getting-started.md \
  docs/for-developers/architecture-overview.md \
  docs/for-developers/service-internals/api-gateway.md \
  docs/for-developers/service-internals/integration-layer.md \
  docs/for-developers/service-internals/orchestration-layer.md \
  docs/for-developers/service-internals/knowledge-layer.md \
  docs/for-developers/service-internals/execution-engine.md \
  docs/for-developers/service-internals/learning-engine.md \
  docs/for-developers/service-internals/auth-service.md \
  docs/for-developers/service-internals/admin-service.md \
  docs/for-developers/service-internals/agent-service.md \
  docs/for-developers/service-internals/itsm-connector.md \
  docs/for-developers/sdk/overview.md \
  docs/for-developers/sdk/synapto-cicd.md \
  docs/for-developers/sdk/synapto-classifier.md \
  docs/for-developers/sdk/synapto-detector.md \
  docs/for-developers/sdk/synapto-remediator.md \
  docs/for-developers/sdk/synapto-telemetry.md \
  docs/for-developers/database-schema.md \
  docs/for-developers/adding-a-service.md \
  docs/for-developers/contracts.md \
  docs/reference/api.md \
  docs/reference/configuration.md \
  docs/reference/changelog.md; do
    echo "# $(basename $f .md | tr '-' ' ' | sed 's/\b./\u&/g')" > "$f"
done
```

- [ ] **Step 1.6: Verify the site builds**

```bash
mkdocs build --strict 2>&1
```

Expected: `INFO - Documentation built in X.X seconds` with no warnings or errors.

- [ ] **Step 1.7: Commit**

```bash
git add mkdocs.yml requirements-docs.txt docs/index.md docs/for-operators/ docs/for-developers/ docs/reference/
git commit -m "docs: add MkDocs scaffold with full nav and placeholder pages"
```

---

## Task 2: Operator Pages — Setup & Auth

**Files:**
- Write: `docs/for-operators/getting-started.md`
- Write: `docs/for-operators/default-credentials.md`

- [ ] **Step 2.1: Write `docs/for-operators/getting-started.md`**

```markdown
# Getting Started

Synapto runs entirely in Docker. You need Docker, Docker Compose v2+, and a `.env` file. No other dependencies.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2+
- Git
- A terminal with `bash` or `zsh`

## 1. Clone the repository

```bash
git clone https://github.com/adumenica/Synapto.git
cd Synapto
```

## 2. Create the environment file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

| Variable | What to set |
|----------|-------------|
| `SECRET_KEY` | A random 64-character string. Generate with `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | A strong database password |
| `REDIS_PASSWORD` | A strong Redis password |
| `ADMIN_DEFAULT_PASSWORD` | The password for the initial admin user |
| `ENCRYPTION_KEY` | A 32-byte Fernet key. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

See [Configuration Reference](../reference/configuration.md) for the full variable list.

## 3. Start all services

```bash
docker compose up -d --build
```

The first build takes 3–5 minutes while Docker pulls base images and installs Python dependencies.

## 4. Verify all services are healthy

```bash
docker compose ps
```

All containers should show `healthy` or `running`. If a service shows `unhealthy`, check its logs:

```bash
docker compose logs <service-name> --tail 50
```

## 5. Access the platform

| Interface | URL |
|-----------|-----|
| Web UI | `http://localhost:3000` |
| API (Swagger) | `http://localhost:8000/docs` |

Log in with the credentials from [Default Credentials](default-credentials.md).

## Updating

To pull the latest code and rebuild:

```bash
git pull
docker compose up -d --build
```

Database migrations run automatically on startup — no manual steps needed.

!!! tip "Troubleshooting"
    If the frontend shows a blank page, run `docker compose logs selfhealing-frontend --tail 20`. A "cannot find module" error usually means the node_modules cache is stale — run `docker compose build --no-cache frontend`.
```

- [ ] **Step 2.2: Write `docs/for-operators/default-credentials.md`**

```markdown
# Default Credentials

On first startup, Synapto creates one admin user automatically if `ADMIN_DEFAULT_PASSWORD` is set in `.env`.

## Default admin account

| Field | Value |
|-------|-------|
| Username | `admin` |
| Role | `admin` |
| Password | Value of `ADMIN_DEFAULT_PASSWORD` in your `.env` |

!!! warning "Change this immediately"
    Log in and change the admin password before exposing the platform to a network. The default account has full admin privileges.

## How to change the password

1. Log in to the Web UI at `http://localhost:3000`.
2. Click your username in the top-right corner → **Profile**.
3. Enter your current password and the new password, then click **Save**.

Or via API:

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/admin \
  -H "Content-Type: application/json" \
  --cookie "access_token=<your_token>" \
  -d '{"password": "your-new-secure-password"}'
```

## Creating additional users

Operators and admins can create users in the Admin panel:

1. Navigate to **Admin → Users**.
2. Click **New User**.
3. Set username, password, and role (`viewer`, `operator`, or `admin`).

## Roles

| Role | Capabilities |
|------|-------------|
| `viewer` | Read-only access to incidents, events, executions, and analytics |
| `operator` | All viewer capabilities plus: approve remediations, trigger executions, manage playbooks |
| `admin` | All operator capabilities plus: manage users, credentials, AI settings, ITSM, SSO, licensing |

!!! tip "Troubleshooting"
    If no admin user was created on first startup, check that `ADMIN_DEFAULT_PASSWORD` is set in `.env` and that the `auth-service` container started without errors (`docker compose logs selfhealing-auth --tail 30`).
```

- [ ] **Step 2.3: Verify build**

```bash
mkdocs build --strict 2>&1
```

Expected: no errors.

- [ ] **Step 2.4: Commit**

```bash
git add docs/for-operators/getting-started.md docs/for-operators/default-credentials.md
git commit -m "docs(operators): add getting-started and default-credentials pages"
```

---

## Task 3: Operator Pages — Webhook Integrations

**Files:**
- Write: `docs/for-operators/webhook-integrations.md`

- [ ] **Step 3.1: Write `docs/for-operators/webhook-integrations.md`**

```markdown
# Webhook Integrations

Synapto ingests alerts from external monitoring systems via a single public HTTP endpoint. No authentication is required on this endpoint — monitoring tools typically cannot issue JWTs.

**Ingestion endpoint:** `POST http://<host>:8000/api/v1/events`

All payloads must include at minimum: `source`, `event_type`, `severity`, `title`. Additional fields (hostname, labels) improve classification accuracy.

---

## Prometheus AlertManager

Add a receiver to your `alertmanager.yml`:

```yaml
receivers:
  - name: synapto
    webhook_configs:
      - url: "http://<synapto-host>:8000/api/v1/events"
        send_resolved: true
```

Add a route to send critical alerts to Synapto:

```yaml
route:
  receiver: synapto
  routes:
    - match:
        severity: critical
      receiver: synapto
```

Synapto auto-detects the Prometheus payload format and extracts `alertname`, `instance`, `severity`, and labels.

---

## Zabbix

In Zabbix, create a **Webhook** media type:

- **URL:** `http://<synapto-host>:8000/api/v1/events`
- **HTTP method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**

```json
{
  "source": "zabbix",
  "event_type": "{TRIGGER.NAME}",
  "severity": "{TRIGGER.SEVERITY}",
  "title": "{TRIGGER.NAME} on {HOST.NAME}",
  "hostname": "{HOST.NAME}",
  "labels": {
    "problem": "{EVENT.NAME}",
    "trigger_id": "{TRIGGER.ID}"
  }
}
```

---

## Dynatrace

In Dynatrace, create an **Alerting Profile** and a **Problem Notification** of type **Custom Integration**:

- **URL:** `http://<synapto-host>:8000/api/v1/events`
- **Content-Type:** `application/json`
- **Payload:**

```json
{
  "source": "dynatrace",
  "event_type": "{ProblemTitle}",
  "severity": "{State}",
  "title": "{ProblemTitle}",
  "hostname": "{ImpactedEntity}",
  "labels": {
    "problem_id": "{ProblemID}",
    "root_cause": "{ProblemDetailsText}"
  }
}
```

---

## CloudWatch (via SNS + Lambda)

CloudWatch does not support direct HTTP webhooks. Route via an SNS topic → Lambda function that POSTs to Synapto:

```python
import json, urllib.request

def lambda_handler(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    payload = json.dumps({
        "source": "cloudwatch",
        "event_type": message.get("AlarmName", "unknown"),
        "severity": "critical" if message.get("NewStateValue") == "ALARM" else "info",
        "title": message.get("AlarmDescription", message.get("AlarmName")),
        "hostname": message.get("Trigger", {}).get("Dimensions", [{}])[0].get("value", "unknown"),
        "labels": {"region": message.get("Region", ""), "account": message.get("AWSAccountId", "")}
    }).encode()
    req = urllib.request.Request(
        "http://<synapto-host>:8000/api/v1/events",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req)
```

---

## Generic Webhook

Any system that can POST JSON:

```bash
curl -X POST http://<host>:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "custom",
    "event_type": "service_down",
    "severity": "critical",
    "title": "Nginx is not responding on web-01",
    "hostname": "web-01",
    "labels": {"service": "nginx", "env": "production"}
  }'
```

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Identifier of the alerting system |
| `event_type` | string | Machine-readable event type (e.g. `high_cpu`, `disk_full`) |
| `severity` | string | `critical`, `high`, `medium`, `low`, or `info` |
| `title` | string | Human-readable alert title |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| `hostname` | string | Affected host (used for topology lookup and credential matching) |
| `description` | string | Detailed alert description |
| `labels` | object | Key-value pairs passed through to the incident |

!!! tip "Troubleshooting"
    If events are ingested (you get a 201 response) but no incident appears, check the Orchestration Layer logs: `docker compose logs selfhealing-orchestration --tail 50`. The most common cause is a Redis Stream not being consumed — verify the consumer group exists with `docker compose exec redis redis-cli XINFO GROUPS events`.
```

- [ ] **Step 3.2: Verify build**

```bash
mkdocs build --strict 2>&1
```

- [ ] **Step 3.3: Commit**

```bash
git add docs/for-operators/webhook-integrations.md
git commit -m "docs(operators): add webhook integrations page"
```

---

## Task 4: Operator Pages — Core Workflows

**Files:**
- Write: `docs/for-operators/incident-management.md`
- Write: `docs/for-operators/playbooks-and-policies.md`
- Write: `docs/for-operators/credential-vault.md`

- [ ] **Step 4.1: Write `docs/for-operators/incident-management.md`**

```markdown
# Incident Management

The **Incidents** page (`/incidents`) is the primary operator view. It shows all incidents in real time via a Server-Sent Events (SSE) stream — no manual refreshing needed.

## Incident lifecycle

```
open → investigating → remediating → resolved → closed
```

| Status | Meaning |
|--------|---------|
| `open` | Event received, incident created, not yet being processed |
| `investigating` | Orchestration Layer is running diagnostics |
| `remediating` | Remediation scripts are executing |
| `resolved` | Execution succeeded and the incident is closed automatically |
| `closed` | Manually closed by an operator |

## Real-time updates

The Incidents page connects to `GET /api/v1/incidents/stream` on load. New incidents and status changes appear in the table immediately — no polling, no page refresh.

If the connection drops (network interruption), the UI reconnects automatically with exponential backoff.

## Incident detail panel

Click any row to open the detail panel. It shows:

- Full incident metadata (severity, hostname, infrastructure layer, component)
- Timeline of status transitions
- Linked execution results (stdout, stderr, exit code)
- The playbook that was used
- AI promotion banner (if the incident was resolved by AI — see [Action Catalogue](action-catalogue.md))

## Manually closing an incident

If an incident is resolved outside the platform (e.g., you fixed it manually), click **Close** in the detail panel. This sets `status=closed` and stops any running executions for that incident.

## Approving a remediation

If a policy requires approval (`APPROVAL_REQUIRED` mode), the incident detail panel shows an **Approve** button. Only users with the `operator` or `admin` role can approve.

!!! tip "Troubleshooting"
    If the real-time stream shows "Disconnected" in the UI header, check the API Gateway logs for SSE errors: `docker compose logs selfhealing-gateway --tail 30`. The stream requires Redis to be healthy — verify with `docker compose exec redis redis-cli ping`.
```

- [ ] **Step 4.2: Write `docs/for-operators/playbooks-and-policies.md`**

```markdown
# Playbooks & Policies

**Playbooks** define what steps to take when an incident occurs. **Policies** map incident conditions to playbooks and set execution mode.

## Playbooks

A playbook is an ordered list of steps. Each step has:

| Field | Description |
|-------|-------------|
| `name` | Human-readable step name |
| `category` | `diagnostic`, `remediation`, `cleanup`, or `monitoring` |
| `script_id` | ID of the script in the Script Library to run |
| `order` | Execution order (lower = first) |

### Creating a playbook

1. Navigate to **Playbooks** in the sidebar.
2. Click **New Playbook**.
3. Give it a name and description.
4. Add steps: select a category, choose a script from the library, set the order.
5. Click **Save**.

### Playbook matching

The Orchestration Layer finds the right playbook in three tiers (in order):

1. **Exact match** — a Policy maps this specific incident type to a playbook.
2. **SOP similarity** — Jaccard token overlap between the incident title and SOP titles (threshold: 0.5).
3. **AI generation** — if tiers 1 and 2 both miss, the Learning Engine generates a new playbook and SOP.

## Policies

A policy controls which playbook runs for which incidents, and how.

### Execution modes

| Mode | Behaviour |
|------|-----------|
| `STANDARD` | Run all playbook steps automatically |
| `DIAGNOSTIC_ONLY` | Run diagnostic steps only; skip remediation |
| `APPROVAL_REQUIRED` | Pause before remediation; wait for operator approval |

### Creating a policy

1. Navigate to **Policies** in the sidebar.
2. Click **New Policy**.
3. Set the matching criteria (event type, severity, hostname pattern).
4. Select the target playbook.
5. Choose an execution mode.
6. Click **Save**.

A default policy (`Critical Event Auto-Remediation`) is seeded on first startup and applies `STANDARD` mode to all critical events.

!!! tip "Troubleshooting"
    If the Orchestration Layer is skipping your policy, confirm the incident's `event_type` and `severity` exactly match the policy's criteria — matching is case-sensitive. Check the Orchestration logs for the phrase `policy match` to see which policy (if any) was selected.
```

- [ ] **Step 4.3: Write `docs/for-operators/credential-vault.md`**

```markdown
# Credential Vault

The Credential Vault stores the credentials the Execution Engine uses to connect to target infrastructure. All credentials are encrypted at rest using a Fernet key (`ENCRYPTION_KEY` in `.env`).

## Supported credential types

| Type | Used for |
|------|---------|
| SSH | Linux/Unix hosts via `paramiko` |
| WinRM | Windows hosts via `pywinrm` (NTLM auth) |
| Netmiko | Network devices (Cisco, Juniper, Arista, etc.) |
| SQL | Databases (MSSQL via `pymssql`, MySQL via `pymysql`) |

## Adding a credential

1. Navigate to **Admin → Credentials**.
2. Click **New Credential**.
3. Select the type, enter the hostname (or IP), username, and password (or SSH key for SSH type).
4. Click **Save**.

The credential is encrypted before being written to the database. The plaintext is never logged.

## How credentials are resolved

When the Execution Engine receives a job, it looks up the credential for the target host using this priority:

1. Exact hostname match
2. Wildcard match (e.g., a credential for `web-*` matches `web-01`)
3. Default credential for the credential type

If no match is found, the execution fails with a `CREDENTIAL_NOT_FOUND` error.

## Rotating a credential

Edit the credential in **Admin → Credentials** and enter the new password. Existing running executions are not affected — they use the credential value that was resolved at the time the job started.

!!! tip "Troubleshooting"
    If executions fail with `Authentication failed`, verify the credential hostname matches the `target_host` value shown in the Execution detail. Check the Execution Engine logs: `docker compose logs selfhealing-execution --tail 30`.
```

- [ ] **Step 4.4: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-operators/incident-management.md docs/for-operators/playbooks-and-policies.md docs/for-operators/credential-vault.md
git commit -m "docs(operators): add incident management, playbooks/policies, credential vault pages"
```

---

## Task 5: Operator Pages — New Features & Integrations

**Files:**
- Write: `docs/for-operators/action-catalogue.md`
- Write: `docs/for-operators/cicd-risk.md`
- Write: `docs/for-operators/service-health.md`
- Write: `docs/for-operators/ai-configuration.md`
- Write: `docs/for-operators/itsm-integration.md`
- Write: `docs/for-operators/sso-configuration.md`

- [ ] **Step 5.1: Write `docs/for-operators/action-catalogue.md`**

```markdown
# Action Catalogue

The **Action Catalogue** (`/catalogue`) is the curated library of proven remediation scripts. Every script here has been either human-authored or AI-generated and then promoted by an operator — it is safe to reuse without AI involvement.

## Browsing the catalogue

The catalogue shows a filterable table with columns: Name, Category, Language, Promoted (date), and Actions.

Filter by:
- **Search** — matches script name
- **Category** — `diagnostic`, `remediation`, `cleanup`, `monitoring`
- **Language** — `Python`, `Bash`, `PowerShell`, `Shell`

Click any row to open the script drawer. The drawer shows:
- Script metadata (category, language, promoted date)
- Full script content in a read-only code editor
- A link to the source incident that produced the script

## Promoting an AI fix to the catalogue

When the Learning Engine generates a fix that successfully resolves an incident, a promotion banner appears at the top of the Incident detail panel:

> "This incident was resolved by AI. Promote the fix to the Action Catalogue?"

Click **Promote to Catalogue** to mark the script as `is_gold_standard = true`. It will then appear in the catalogue and be preferred by the Orchestration Layer's Tier 2 matching on future incidents with similar titles.

## Removing a script from the catalogue

Open the script drawer and click **Remove from Catalogue**. This sets `is_gold_standard = false` — the script is not deleted, just demoted. It can be re-promoted later.

!!! tip "Troubleshooting"
    If the promotion banner does not appear on a resolved incident, check that `incident.meta_data.promotion_eligible` is `true`. This flag is set by the Learning Engine when it generates the fix. If it is missing, confirm the incident was resolved by Tier 3 (AI) and not Tier 1 or 2 — Tier 1/2 resolutions use existing scripts and are not promotion candidates.
```

- [ ] **Step 5.2: Write `docs/for-operators/cicd-risk.md`**

```markdown
# CI/CD Risk Assessment

The **CI/CD Risk** page (`/cicd`) scores a planned deployment for risk before you run it. Fill in the deployment details and the risk score updates live as you type — no submit button needed.

## Risk factors

The scorer weights these factors:

| Factor | Max contribution |
|--------|-----------------|
| Production environment | +0.30 |
| Database migration | +0.30 |
| Large changeset (>30 files) | +0.20 |
| Off-hours deployment | +0.15 |
| No rollback available | +0.15 |
| >2 affected services | +0.10 |

Scores are capped at 1.0. The risk levels are:

| Score | Level | Recommendation |
|-------|-------|----------------|
| 0.0–0.29 | Low | Deploy with standard monitoring |
| 0.30–0.59 | Medium | Deploy during business hours with enhanced monitoring |
| 0.60–0.79 | High | Requires manual approval and rollback plan |
| 0.80–1.0 | Critical | Requires senior engineer approval, staged rollout, and war room |

## Using the page

1. Navigate to **CI/CD Risk** in the sidebar.
2. Fill in the deployment form (left column):
   - **Service name** — the service being deployed
   - **Environment** — development / staging / production
   - **Changed files** — number of files changed in the PR
   - **Affected services** — comma-separated list of downstream services
   - **DB migration** — toggle on if the deployment includes a schema migration
   - **Off-hours** — toggle on if deploying outside business hours
   - **Rollback available** — toggle on if you have a tested rollback procedure (default: on)
   - **Commit message** — optional, for your records
3. The right panel shows the risk score, level badge, contributing factors, and a recommendation.

If the score is ≥ 0.6, a **"Manual approval required"** warning appears.

!!! tip "Troubleshooting"
    If the risk panel stays empty after filling in fields, check the browser network tab for a failed `POST /api/v1/cicd/risk-assessment`. Ensure the API Gateway container is healthy and your session cookie is valid (log out and back in if needed).
```

- [ ] **Step 5.3: Write `docs/for-operators/service-health.md`**

```markdown
# Service Health

The **Service Health** widget on the Dashboard gives a live snapshot of response times across your monitored services. It shows a sparkline (mini trend chart) of the last 10 response time samples for each service.

## What the widget shows

Each service card displays:
- Service name
- Current status badge: **Healthy** (green), **Degraded** (amber), or **Down** (red)
- A sparkline of recent response times (last 10 samples)
- The most recent response time in milliseconds

Status is determined by response time thresholds:

| Status | Threshold |
|--------|-----------|
| Healthy | p95 response time < 500 ms |
| Degraded | p95 response time 500 ms–2000 ms |
| Down | Service unreachable or p95 > 2000 ms |

## Data source

Response time data is published to the `synapto:telemetry` Redis Stream by the `synapto-telemetry` library instrumented in each backend service. The Dashboard's `healthApi` polls `GET /api/v1/health/services` every 30 seconds.

## What to do when a service shows Degraded or Down

A degraded or down service in the widget means Synapto's own backend services are affected, not your monitored infrastructure. Check:

```bash
docker compose ps
docker compose logs <service-name> --tail 50
```

If the service is healthy in Docker but the widget still shows degraded, the telemetry data may be stale — check Redis: `docker compose exec redis redis-cli XLEN synapto:telemetry`.
```

- [ ] **Step 5.4: Write `docs/for-operators/ai-configuration.md`**

```markdown
# AI Configuration

Synapto uses AI for Tier 3 playbook generation, incident analysis, and script learning. You configure the AI provider and API key from the Admin panel.

## Supported providers

| Provider | Model used |
|----------|-----------|
| Anthropic Claude | `claude-3-5-sonnet-20241022` |
| OpenAI | GPT-4o |
| Google | Gemini 1.5 Pro |

## Setting up the AI provider

1. Navigate to **Admin → AI Settings**.
2. Select your provider.
3. Enter your API key.
4. Click **Save**.

The API key is encrypted using your `ENCRYPTION_KEY` before being stored in the database.

## Testing the connection

After saving, click **Test Connection**. Synapto sends a minimal prompt to the provider and reports success or the error returned.

## How AI is used

| Feature | Trigger |
|---------|---------|
| Incident analysis | Tier 3 only — when no playbook or SOP matches |
| SOP generation | Alongside incident analysis — the generated SOP is saved for future reuse |
| Composite script generation | Merges multiple playbook steps into a single script to reduce SSH connections |
| Analytics recommendations | Background job that analyses historical incident data |

## Cost management

Synapto calls AI only on Tier 3 misses. If your SOP library covers common incidents well, AI usage is low. The Admin panel shows a usage counter for AI calls in the current billing period.

!!! tip "Troubleshooting"
    If AI generation fails with a 502 error on the Learning Engine, check the Learning Engine logs: `docker compose logs selfhealing-learning --tail 30`. A `401 Unauthorized` from the AI provider means the API key is wrong. A `429 Too Many Requests` means your provider rate limit is exhausted.
```

- [ ] **Step 5.5: Write `docs/for-operators/itsm-integration.md`**

```markdown
# ITSM Integration

Synapto can automatically create and update tickets in your ITSM system when incidents are created or resolved. ITSM integration is optional.

## Supported systems

- ServiceNow
- Jira (Cloud and Server)
- BMC Remedy

## Configuring an ITSM integration

1. Navigate to **Admin → Integrations**.
2. Click **New Integration** and select your ITSM system.
3. Fill in the connection details:

=== "ServiceNow"
    | Field | Value |
    |-------|-------|
    | Instance URL | `https://<your-instance>.service-now.com` |
    | Username | ServiceNow username with `incident_manager` role |
    | Password | ServiceNow password |
    | Table | `incident` (default) |

=== "Jira"
    | Field | Value |
    |-------|-------|
    | Base URL | `https://<your-instance>.atlassian.net` |
    | Email | Jira account email |
    | API Token | Generate at `id.atlassian.com/manage-profile/security/api-tokens` |
    | Project Key | Jira project key (e.g. `OPS`) |
    | Issue Type | `Incident` or `Bug` |

=== "BMC Remedy"
    | Field | Value |
    |-------|-------|
    | Server URL | `http://<remedy-server>:8008` |
    | Username | Remedy username |
    | Password | Remedy password |

4. Click **Test Connection**, then **Save** if the test passes.

## How it works

When the Orchestration Layer creates an incident, it calls the ITSM Connector. If an active integration is configured, the connector creates a ticket in the external system and stores the `external_ticket_id` on the Incident record.

When the incident resolves, the connector updates the ticket status to resolved/closed.

!!! tip "Troubleshooting"
    If tickets are not being created, check the ITSM Connector logs: `docker compose logs selfhealing-itsm --tail 30`. The connector is optional — if the container is not running, the platform operates normally without ITSM sync.
```

- [ ] **Step 5.6: Write `docs/for-operators/sso-configuration.md`**

```markdown
# SSO Configuration

Synapto supports Single Sign-On via OIDC (OpenID Connect). Once configured, users can log in with their organisation's identity provider instead of a local password.

## Supported providers

Any OIDC-compliant provider, including:
- Microsoft Entra ID (Azure AD)
- Okta
- Google Workspace
- Keycloak
- Auth0

## Setting up OIDC

1. In your identity provider, create a new **OIDC application** (or OAuth2 app):
   - **Redirect URI:** `http://<synapto-host>:8000/auth/callback`
   - **Scopes:** `openid email profile`
   - Note the **Client ID** and **Client Secret**.

2. In Synapto, navigate to **Admin → SSO**.
3. Fill in the OIDC details:

   | Field | Description |
   |-------|-------------|
   | Provider Name | Display name shown on the login button |
   | Client ID | From your identity provider |
   | Client Secret | From your identity provider |
   | Discovery URL | The OIDC discovery endpoint, e.g. `https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration` |
   | Default Role | Role assigned to new users on first login (`viewer` recommended) |

4. Click **Save**. A **Sign in with [Provider]** button appears on the login page.

## User provisioning

On first SSO login, Synapto creates a local user account with the email from the OIDC token. The default role is set to whatever you configured. Admins can change individual user roles in **Admin → Users** after provisioning.

## Disabling local login

If you want to enforce SSO-only login, set `FORCE_SSO=true` in `.env` and restart the Auth Service. Local password authentication will be disabled — ensure your SSO connection is working before doing this.

!!! tip "Troubleshooting"
    If login redirects back to the login page with no error, check the Auth Service logs for OIDC callback errors: `docker compose logs selfhealing-auth --tail 30`. The most common cause is a mismatched redirect URI — verify it matches exactly, including the trailing slash (or lack thereof).
```

- [ ] **Step 5.7: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-operators/action-catalogue.md docs/for-operators/cicd-risk.md docs/for-operators/service-health.md docs/for-operators/ai-configuration.md docs/for-operators/itsm-integration.md docs/for-operators/sso-configuration.md
git commit -m "docs(operators): add action catalogue, cicd risk, service health, ai config, itsm, sso pages"
```

---

## Task 6: Developer Pages — Getting Started & Architecture

**Files:**
- Write: `docs/for-developers/getting-started.md`
- Write: `docs/for-developers/architecture-overview.md`

- [ ] **Step 6.1: Write `docs/for-developers/getting-started.md`**

```markdown
# Developer Getting Started

## Prerequisites

- Python 3.11+
- Docker and Docker Compose v2+
- Node.js 18+ (for frontend)

## Running services locally

All services are Python FastAPI applications. The recommended dev workflow is:

1. Start infrastructure (Postgres + Redis) in Docker.
2. Run the specific service you're working on locally.
3. Let everything else run in Docker.

```bash
# Start only infrastructure
docker compose up -d postgres redis

# Set up a virtualenv for the service you're editing
cd backend/<service-name>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set env vars (copy from docker-compose.yml for that service)
export DATABASE_URL=postgresql://synapto:changeme@localhost:5432/synapto
export REDIS_URL=redis://:changeme-redis-password@localhost:6379
export SECRET_KEY=dev-secret-key

# Run the service
uvicorn main:app --reload --port <service-port>
```

## Running the frontend locally

```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:5173
```

The frontend Vite dev server proxies API requests to `http://localhost:8000` (the API Gateway). Make sure the API Gateway is running.

## Running all services in Docker (full stack)

```bash
docker compose up -d --build
```

## Installing the Python libraries

The AIOps libraries in `libs/` are pip-installable in editable mode:

```bash
pip install -e libs/synapto-contracts
pip install -e libs/synapto-telemetry
pip install -e libs/synapto-cicd
# etc.
```

Or install the meta-package (pulls in all libs):

```bash
pip install -e libs/synapto-sdk
```

## Shared module

`backend/shared/` contains code used by all Python services: database setup, auth helpers, Redis utilities, Pydantic schemas. It is installed into each service's Docker image automatically (it's mounted as a volume in development).

## Running tests

Each library in `libs/` has a `tests/` directory:

```bash
cd libs/synapto-cicd
pytest tests/ -v
```

Backend services do not currently have unit test suites — integration testing is done by running the full stack and posting events to the API.
```

- [ ] **Step 6.2: Write `docs/for-developers/architecture-overview.md`**

Content migrated and refined from `docs/architecture/system_design.md` Part 1 (lines 1–108) and Part 2 section 2 (end-to-end data flow). Write the file:

```markdown
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
```

- [ ] **Step 6.3: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-developers/getting-started.md docs/for-developers/architecture-overview.md
git commit -m "docs(developers): add getting-started and architecture-overview pages"
```

---

## Task 7: Developer Service Internals — Original Six Services

**Files:**
- Write: `docs/for-developers/service-internals/api-gateway.md`
- Write: `docs/for-developers/service-internals/integration-layer.md`
- Write: `docs/for-developers/service-internals/orchestration-layer.md`
- Write: `docs/for-developers/service-internals/knowledge-layer.md`
- Write: `docs/for-developers/service-internals/execution-engine.md`
- Write: `docs/for-developers/service-internals/learning-engine.md`

Source: content comes from `docs/architecture/system_design.md` sections 1.1–1.6. The content below is the extracted, reformatted version — do not read the source file again, use what is written here.

- [ ] **Step 7.1: Write `docs/for-developers/service-internals/api-gateway.md`**

```markdown
# API Gateway

**File:** `backend/api-gateway/main.py`  
**Port:** 8000 (the only publicly exposed backend port)

The API Gateway is the single entry point for all client requests — from the browser and from external monitoring systems. It contains no business logic; it is a routing, authentication, and rate-limiting proxy.

## Responsibilities

- **Authentication** — validates the JWT access token (HttpOnly cookie `access_token`) on every protected route via `get_current_user()`. Unauthenticated requests receive a 401.
- **Role-based access** — `require_operator` and `require_admin` decorators enforce role checks per endpoint.
- **Service routing** — uses `httpx` to forward requests to the appropriate backend service. Backend URLs are read from environment variables.
- **Rate limiting** — `slowapi` caps login attempts at 5/min per IP.
- **CORS** — allows the frontend origin (from `CORS_ORIGINS` env var).
- **Retry logic** — `tenacity` exponential backoff (3 attempts, 1–32 s) on outgoing calls.
- **API docs** — Swagger at `/docs`, Redoc at `/redoc`.
- **SSE stream** — `GET /api/v1/incidents/stream` reads from the Redis `events` stream and pushes `text/event-stream` to connected browsers.

## Design note

JWT validation is centralised here in `backend/shared/auth.py`. Backend microservices trust requests forwarded by the Gateway and do not re-validate tokens, keeping security logic in one place.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Signs and verifies JWTs |
| `CORS_ORIGINS` | Comma-separated list of allowed origins |
| `INTEGRATION_SERVICE_URL` | URL of the Integration Layer |
| `ORCHESTRATION_SERVICE_URL` | URL of the Orchestration Layer |
| `KNOWLEDGE_SERVICE_URL` | URL of the Knowledge Layer |
| `EXECUTION_SERVICE_URL` | URL of the Execution Engine |
| `LEARNING_SERVICE_URL` | URL of the Learning Engine |
| `AUTH_SERVICE_URL` | URL of the Auth Service |
| `ADMIN_SERVICE_URL` | URL of the Admin Service |
| `REDIS_URL` | Redis connection string (for SSE stream) |
```

- [ ] **Step 7.2: Write `docs/for-developers/service-internals/integration-layer.md`**

```markdown
# Integration Layer

**File:** `backend/integration-layer/main.py`  
**Port:** 8001

The Integration Layer is the "ears" of the platform — it receives raw alerts from external monitoring systems and converts them into the internal Event format.

## How it works

1. External tools POST to `POST /api/v1/events` (this endpoint is **public** — no auth required).
2. The layer detects the source type (Prometheus, CloudWatch, Zabbix, Dynatrace, Azure Monitor, custom) and extracts relevant fields.
3. A new `Event` record is written to PostgreSQL.
4. The event ID and metadata are published to the Redis Stream `events`.
5. The caller receives a 201 with the event ID.

## Why Redis Streams?

Publishing to a stream decouples ingestion from processing. The Integration Layer returns immediately; the Orchestration Layer processes at its own pace and can replay messages on restart.

## Supported sources

`prometheus`, `zabbix`, `dynatrace`, `cloudwatch`, `azure_monitor`, and a generic `custom` format.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
```

- [ ] **Step 7.3: Write `docs/for-developers/service-internals/orchestration-layer.md`**

```markdown
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
```

- [ ] **Step 7.4: Write `docs/for-developers/service-internals/knowledge-layer.md`**

```markdown
# Knowledge Layer

**File:** `backend/knowledge-layer/main.py`  
**Port:** 8003

The Knowledge Layer is the "library" — a pure CRUD service for all configuration data that drives the platform's decisions.

## What it stores

| Resource | Description |
|----------|-------------|
| **Policies** | Rules mapping incident conditions to playbooks and execution modes |
| **Playbooks** | Ordered lists of remediation steps (stored as JSONB) |
| **Scripts** | Reusable code snippets (Python, Bash, PowerShell, Shell) |
| **SOPs** | Human-readable Standard Operating Procedures (Markdown) |
| **Network Topology** | Known hosts: hostname, IP, OS family, type, dependencies |

## Key endpoint

`POST /playbooks/match` — takes an incident title, returns the best matching playbook ID. This is Tier 1 of the Orchestration Layer's matching logic.

The `is_gold_standard` flag on scripts indicates an AI-generated fix that has been promoted to the Action Catalogue. The Orchestration Layer's Tier 2 matching prefers gold-standard SOPs.

## Seeding

On first startup, the Knowledge Layer seeds a default "Critical Event Auto-Remediation" policy so the platform works out of the box without any configuration.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
```

- [ ] **Step 7.5: Write `docs/for-developers/service-internals/execution-engine.md`**

```markdown
# Execution Engine

**File:** `backend/execution-engine/main.py`  
**Port:** 8004

The Execution Engine is the "hands" — it safely runs scripts on target infrastructure. All execution is asynchronous: the caller receives an execution ID immediately and polls for the result.

## Supported execution methods

| Method | Target | Library |
|--------|--------|---------|
| SSH | Linux/Unix hosts | `paramiko` |
| WinRM | Windows hosts | `pywinrm` (NTLM auth) |
| Netmiko | Network devices (Cisco, Juniper, etc.) | `netmiko` |
| SQL | Databases | `pymssql` / `pymysql` |
| Docker | Local sandboxed execution | Docker SDK |

## Execution flow

1. Receive `POST /execute` with script content, language, and target host.
2. Look up credentials for the target host from the encrypted credential vault.
3. Mark execution as `RUNNING` in the database.
4. Execute the script (SSH, or Docker container for local/sandbox runs).
5. Capture stdout, stderr, exit code, and timing.
6. Write results to the `executions` table.

## Supported script languages

`PYTHON`, `BASH`, `POWERSHELL`, `SHELL`

## Docker images for sandboxed execution

| Language | Image |
|----------|-------|
| Python | `python:3.11-alpine` |
| PowerShell | `mcr.microsoft.com/powershell:lts-alpine-3.14` |
| Bash/Shell | `alpine:latest` |

## Security hardening

The Execution Engine container runs with:
- Read-only root filesystem
- All Linux capabilities dropped except `DAC_OVERRIDE`
- No new privileges flag
- 100 MB tmpfs at `/tmp` for script staging

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Fernet key for decrypting credentials |
| `AGENT_SERVICE_URL` | Agent Service URL (for agent-based execution) |
| `INTERNAL_SERVICE_SECRET` | Shared secret for Agent Service internal calls |
```

- [ ] **Step 7.6: Write `docs/for-developers/service-internals/learning-engine.md`**

```markdown
# Learning Engine

**File:** `backend/learning-engine/main.py`  
**Port:** 8005

The Learning Engine provides all AI-driven capabilities and platform analytics.

## AI endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /analyze` | Analyses an incident and predicts root cause |
| `POST /generate-diagnostic` | Generates a new SOP + diagnostic playbook from an incident description |
| `POST /generate-composite-script` | Merges multiple playbook steps into a single unified script |
| `GET /analytics` | Returns success rates, MTTR, incident counts, top incident types |
| `GET /recommendations` | Suggests improvements based on historical data |

## Supported AI providers

| Provider | Model |
|----------|-------|
| Anthropic Claude (primary) | `claude-3-5-sonnet-20241022` |
| OpenAI | GPT-4o |
| Google | Gemini 1.5 Pro |

The active provider and API key are configured via the Admin panel and stored encrypted in `ai_settings`.

## The learning loop

1. Execution Engine successfully runs an AI-generated script.
2. Orchestration Layer calls `POST /incidents/{id}/promote`.
3. Learning Engine sets `is_gold_standard=true` on the SOP.
4. On the next similar incident, Orchestration Layer's Tier 2 finds the SOP and skips AI generation — saving time and cost.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | For decrypting AI API keys stored in the DB |
```

- [ ] **Step 7.7: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-developers/service-internals/api-gateway.md \
        docs/for-developers/service-internals/integration-layer.md \
        docs/for-developers/service-internals/orchestration-layer.md \
        docs/for-developers/service-internals/knowledge-layer.md \
        docs/for-developers/service-internals/execution-engine.md \
        docs/for-developers/service-internals/learning-engine.md
git commit -m "docs(developers): add service internals for original six services"
```

---

## Task 8: Developer Service Internals — Auth, Admin, Agent, ITSM

**Files:**
- Write: `docs/for-developers/service-internals/auth-service.md`
- Write: `docs/for-developers/service-internals/admin-service.md`
- Write: `docs/for-developers/service-internals/agent-service.md`
- Write: `docs/for-developers/service-internals/itsm-connector.md`

- [ ] **Step 8.1: Write `docs/for-developers/service-internals/auth-service.md`**

```markdown
# Auth Service

**File:** `backend/auth-service/main.py`  
**Port:** 8006

Handles all authentication and session management.

## Login flow

1. Client POSTs credentials to `POST /token` (OAuth2 password flow, `application/x-www-form-urlencoded`).
2. Auth Service validates credentials against the Argon2id-hashed password in `users`.
3. If valid: generates an access token (60 min) and refresh token (7 days) as JWTs.
4. **Both tokens are returned as HttpOnly cookies** (`access_token`, `refresh_token`), not in the response body — JavaScript cannot read them, preventing XSS-based token theft.
5. Token hashes are stored in `oauth_tokens` — allows revocation without a blocklist.

## Other endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /refresh` | Validates refresh token cookie, issues new access token |
| `POST /logout` | Clears both cookies server-side |
| `GET /me` | Returns the current user's profile |

## Default user seeding

On first startup, if no admin user exists and `ADMIN_DEFAULT_PASSWORD` is set, a default admin user is created.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Signs JWTs (must match the value used by the API Gateway) |
| `ADMIN_DEFAULT_PASSWORD` | Password for the seeded admin user |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (default: 60) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (default: 7) |
```

- [ ] **Step 8.2: Write `docs/for-developers/service-internals/admin-service.md`**

```markdown
# Admin Service

**File:** `backend/admin-service/main.py`  
**Port:** 8007

Provides the administrative control plane for the platform.

## Capabilities

| Area | What it manages |
|------|----------------|
| **Users** | Create, update, deactivate users; assign roles |
| **Credentials** | Encrypted vault for SSH, WinRM, Netmiko, SQL credentials |
| **AI Settings** | AI provider selection, encrypted API key storage |
| **ITSM Integrations** | ServiceNow, Jira, BMC Remedy connection config |
| **SSO / External Identity** | OIDC provider configuration (Azure AD, Okta, Keycloak, etc.) |
| **Licensing** | Subscription tier management, usage tracking, on-premise key validation |
| **Audit Logs** | Immutable record of all admin actions (who, what, when, from where) |
| **System Settings** | Global parameters (max execution timeout, max concurrent executions) |

## Encryption

Credentials and AI API keys are encrypted at rest using a Fernet symmetric key (`ENCRYPTION_KEY`). The plaintext is never logged and never stored in plaintext.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Fernet key for encrypting credentials and API keys |
```

- [ ] **Step 8.3: Write `docs/for-developers/service-internals/agent-service.md`**

```markdown
# Agent Service

**Files:** `backend/agent-service/main.py`, `servicer.py`, `auth_interceptor.py`, `enrollment.py`, `signing.py`  
**Port:** 50051 (gRPC) + 8009 (FastAPI internal)

The Agent Service is the bridge between the platform and remotely deployed Synapto agents running on managed nodes. It uses gRPC with mutual TLS (mTLS) — zero-trust: both client and server must present valid certificates.

## Why agents?

When SSH/WinRM is not feasible (firewalls, network segmentation), you can deploy a lightweight Synapto agent on the managed node. The agent connects outbound to port 50051, registers itself, and receives execution jobs via a persistent gRPC stream.

## Security model

- The Agent Service loads a CA certificate, server certificate/key, and an Ed25519 signing key from `/certs/` at startup.
- Every agent must present a certificate signed by the same CA.
- Every job dispatched to an agent is signed with the Ed25519 private key. The agent verifies the signature before executing — this prevents an attacker who intercepts the gRPC stream from injecting fake jobs.
- Agent identity is encoded as a SPIFFE URI: `spiffe://synapto.io/tenant/{tenant_id}/agent/{agent_id}`.

## Enrollment flow

1. Admin generates a one-time enrollment token via the Admin panel.
2. The agent is started on the managed node with the token and the CA certificate.
3. The agent connects to port 50051, presents the token, receives its signed client certificate.
4. The token is consumed and cannot be reused.

## Job dispatch flow

When the Execution Engine routes a job to an agent:

1. Execution Engine calls `POST /dispatch` on the Agent Service's FastAPI interface (internal, protected by `X-Internal-Secret` header).
2. Agent Service validates the target agent exists and is not revoked.
3. Signs the job payload with the Ed25519 private key.
4. Persists the job to the `execution_jobs` table.
5. Pushes the job ID to the Redis Stream `agent-jobs:{agent_id}`.
6. The `AgentBridgeServicer` reads from that stream and delivers the job to the connected agent via its gRPC stream.

## Development mode

If TLS certs are not present and `APP_ENV != production`, the gRPC server starts without mTLS (insecure mode) with a warning. In production, missing certs are fatal.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `INTERNAL_SERVICE_SECRET` | Shared secret for the `/dispatch` endpoint |
| `ED25519_SIGNING_KEY` | Path to the Ed25519 private key (default: `/certs/ed25519_signing.key`) |
| `TLS_SERVER_CERT_PATH` | gRPC server certificate |
| `TLS_SERVER_KEY_PATH` | gRPC server private key |
| `TLS_CA_CERT_PATH` | CA certificate for verifying agent certs |
```

- [ ] **Step 8.4: Write `docs/for-developers/service-internals/itsm-connector.md`**

```markdown
# ITSM Connector

**File:** `backend/itsm-connector/main.py`  
**Port:** 8008

An optional service that creates and updates tickets in external ITSM systems when incidents are created or resolved.

## Supported systems

ServiceNow, Jira (Cloud and Server), BMC Remedy.

## How it integrates

The Orchestration Layer calls the ITSM Connector during incident creation. If an active integration is configured, the connector creates a ticket in the external system and returns the `external_ticket_id`, which is stored on the Incident record for cross-referencing.

When the incident resolves, the Orchestration Layer calls the connector again to close or update the ticket.

## Resilience

The ITSM Connector is optional. If the container is not running or the integration is not configured, the Orchestration Layer logs a warning and continues — ITSM sync failure does not block incident processing.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | For decrypting ITSM credentials stored via Admin Service |
```

- [ ] **Step 8.5: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-developers/service-internals/auth-service.md \
        docs/for-developers/service-internals/admin-service.md \
        docs/for-developers/service-internals/agent-service.md \
        docs/for-developers/service-internals/itsm-connector.md
git commit -m "docs(developers): add service internals for auth, admin, agent, itsm"
```

---

## Task 9: Developer SDK Pages

**Files:**
- Write: `docs/for-developers/sdk/overview.md`
- Write: `docs/for-developers/sdk/synapto-cicd.md`
- Write: `docs/for-developers/sdk/synapto-telemetry.md`
- Write: `docs/for-developers/sdk/synapto-classifier.md`
- Write: `docs/for-developers/sdk/synapto-detector.md`
- Write: `docs/for-developers/sdk/synapto-remediator.md`

- [ ] **Step 9.1: Write `docs/for-developers/sdk/overview.md`**

```markdown
# synapto-sdk Overview

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
```

- [ ] **Step 9.2: Write `docs/for-developers/sdk/synapto-cicd.md`**

```markdown
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
```

- [ ] **Step 9.3: Write `docs/for-developers/sdk/synapto-telemetry.md`**

```markdown
# synapto-telemetry

OpenTelemetry-backed instrumentation library. All 7 Synapto backend services use this library to emit metrics and logs to the `synapto:telemetry` Redis Stream, which feeds the Service Health widget on the Dashboard.

## Install

```bash
pip install -e libs/synapto-telemetry
```

## Classes

### `TelemetryEmitter`

High-level emitter that wraps OTel complexity with Synapto-native methods.

```python
from synapto_telemetry import TelemetryEmitter
import redis.asyncio as aioredis

redis_client = aioredis.from_url("redis://localhost:6379")
emitter = TelemetryEmitter(
    service_name="my-service",
    host="web-server-01",
    redis_client=redis_client,
)

# Emit a metric
emitter.emit_metric("response_time", value=142.3, unit="ms", labels={"endpoint": "/api/v1/events"})

# Emit a log
emitter.emit_log("Processing event abc123", level="INFO", labels={"event_id": "abc123"})
```

### `RedisExporter`

Low-level OTel exporter that writes span data to Redis. Used internally by `TelemetryEmitter`. You typically don't use this directly.

## Data format

Both `emit_metric` and `emit_log` publish a `TelemetrySignal` (from `synapto-contracts`) to the `synapto:telemetry` Redis Stream as JSON:

```json
{
  "signal_id": "<uuid>",
  "source": "my-service",
  "host": "web-server-01",
  "service": "my-service",
  "timestamp": "2026-04-11T10:00:00",
  "metric": {"name": "response_time", "value": 142.3, "unit": "ms"},
  "labels": {"endpoint": "/api/v1/events"}
}
```

## Instrumenting a new service

See [Adding a Service](../adding-a-service.md) for the standard instrumentation pattern used across all Synapto backend services.
```

- [ ] **Step 9.4: Write `docs/for-developers/sdk/synapto-classifier.md`**

```markdown
# synapto-classifier

Six-pass incident classification pipeline. Classifies an incident into one of Synapto's infrastructure layers (OS & Hardware, Network, Database, Middleware, Application).

## Install

```bash
pip install -e libs/synapto-classifier
```

## Usage

```python
from synapto_classifier import ClassifierPipeline
from synapto_contracts import AnomalySignal

pipeline = ClassifierPipeline()
signal = AnomalySignal(title="Nginx 502 errors on web-01", hostname="web-01", severity="high")
classification = pipeline.classify(signal)
print(classification.layer)      # "Middleware"
print(classification.component)  # "nginx"
print(classification.confidence) # 0.87
```

## How it works

The pipeline runs six classification passes in sequence, each specialised for a different infrastructure layer. The pass with the highest confidence score wins. If no pass exceeds the confidence threshold, the incident is classified as `Unknown` and escalated to the Learning Engine for AI classification.
```

- [ ] **Step 9.5: Write `docs/for-developers/sdk/synapto-detector.md`**

```markdown
# synapto-detector

Statistical anomaly detection engine. Analyses time-series metrics to detect anomalies before they become incidents.

## Install

```bash
pip install -e libs/synapto-detector
```

## Usage

```python
from synapto_detector import DetectionEngine
from synapto_contracts import AnomalySignal

engine = DetectionEngine()
# Pass a list of recent metric values (e.g. CPU %)
anomalies = engine.detect(metric_name="cpu_usage", values=[45, 47, 50, 52, 91, 93])
for signal in anomalies:
    print(signal.title)     # "CPU usage anomaly detected"
    print(signal.severity)  # "high"
```

The detector uses Z-score analysis by default. Values more than 3 standard deviations from the rolling mean trigger an `AnomalySignal`.
```

- [ ] **Step 9.6: Write `docs/for-developers/sdk/synapto-remediator.md`**

```markdown
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
```

- [ ] **Step 9.7: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-developers/sdk/
git commit -m "docs(developers): add SDK pages (overview, cicd, telemetry, classifier, detector, remediator)"
```

---

## Task 10: Developer Advanced Pages

**Files:**
- Write: `docs/for-developers/database-schema.md`
- Write: `docs/for-developers/adding-a-service.md`
- Write: `docs/for-developers/contracts.md`

- [ ] **Step 10.1: Write `docs/for-developers/database-schema.md`**

```markdown
# Database Schema

Synapto uses PostgreSQL 15. All tables are created and migrated via Alembic (`backend/migrations/`).

## Core tables

### `events`

Raw alerts received from monitoring tools.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Auto-generated |
| `source` | varchar | `prometheus`, `zabbix`, `cloudwatch`, etc. |
| `event_type` | varchar | Machine-readable event type |
| `severity` | varchar | `critical`, `high`, `medium`, `low`, `info` |
| `title` | text | Human-readable alert title |
| `hostname` | varchar | Affected host (nullable) |
| `description` | text | Alert description (nullable) |
| `labels` | JSONB | Key-value pairs from the source system |
| `created_at` | timestamptz | Ingestion timestamp |

### `incidents`

Correlated groups of related events.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Auto-generated |
| `title` | text | Derived from the triggering event title |
| `status` | varchar | `open`, `investigating`, `remediating`, `resolved`, `closed` |
| `severity` | varchar | Inherited from triggering event |
| `hostname` | varchar | Affected host |
| `layer` | varchar | Infrastructure layer (OS, Network, Database, Middleware, Application) |
| `component` | varchar | Affected component (e.g. `nginx`, `cpu`, `disk`) |
| `playbook_id` | UUID FK | Playbook used for remediation (nullable) |
| `external_ticket_id` | varchar | ITSM ticket ID (nullable) |
| `meta_data` | JSONB | Additional metadata including `promotion_eligible` flag |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

### `executions`

Script execution records.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `incident_id` | UUID FK | Parent incident |
| `script_content` | text | The script that was run |
| `language` | varchar | `PYTHON`, `BASH`, `POWERSHELL`, `SHELL` |
| `target_host` | varchar | Host the script ran on |
| `status` | varchar | `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `TIMEOUT` |
| `stdout` | text | Captured output |
| `stderr` | text | Captured errors |
| `exit_code` | integer | Process exit code |
| `started_at` | timestamptz | |
| `completed_at` | timestamptz | |

### `scripts`

Reusable script library (SOPs and AI-generated).

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `name` | varchar | Human-readable script name |
| `content` | text | Script source code |
| `language` | varchar | Script language |
| `category` | varchar | `diagnostic`, `remediation`, `cleanup`, `monitoring` |
| `is_gold_standard` | boolean | True = promoted to Action Catalogue |
| `created_at` | timestamptz | |

### `playbooks`

Ordered execution plans.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `name` | varchar | |
| `description` | text | |
| `steps` | JSONB | Array of `{name, category, script_id, order}` |

### `policies`

Maps incident conditions to playbooks.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `name` | varchar | |
| `event_type` | varchar | Matching event type (wildcard `*` matches all) |
| `severity` | varchar | Matching severity |
| `hostname_pattern` | varchar | Glob pattern for hostname matching |
| `playbook_id` | UUID FK | |
| `execution_mode` | varchar | `STANDARD`, `DIAGNOSTIC_ONLY`, `APPROVAL_REQUIRED` |

### `users`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `username` | varchar UNIQUE | |
| `hashed_password` | varchar | Argon2id hash |
| `role` | varchar | `viewer`, `operator`, `admin` |
| `is_active` | boolean | |

### `network_topology`

Known infrastructure hosts.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `hostname` | varchar UNIQUE | |
| `ip_address` | varchar | |
| `os_family` | varchar | `linux`, `windows` |
| `host_type` | varchar | `server`, `network_device`, `database`, etc. |
| `dependencies` | JSONB | List of hostnames this host depends on |

## Running migrations

```bash
cd backend
alembic upgrade head
```

Migrations run automatically on service startup in Docker. The Alembic config is at `backend/alembic.ini`.
```

- [ ] **Step 10.2: Write `docs/for-developers/adding-a-service.md`**

```markdown
# Adding a New Service

All Synapto backend services follow the same pattern. This page walks through adding a new FastAPI microservice.

## 1. Create the service directory

```bash
mkdir backend/my-service
touch backend/my-service/main.py
touch backend/my-service/requirements.txt
touch backend/my-service/Dockerfile
```

## 2. Write `main.py`

Follow this template — all existing services use this structure:

```python
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db, get_db
from shared.auth import get_current_user

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="My Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}
```

## 3. Write `requirements.txt`

At minimum:

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
```

Add `synapto-telemetry` if you want to emit metrics to the Service Health dashboard.

## 4. Write the `Dockerfile`

Copy the pattern from any existing service (e.g. `backend/knowledge-layer/Dockerfile`):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../shared /app/shared
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
```

## 5. Add to `docker-compose.yml`

```yaml
my-service:
  build:
    context: ./backend/my-service
    dockerfile: Dockerfile
  container_name: selfhealing-my-service
  environment:
    - SERVICE_NAME=my-service
    - POSTGRES_HOST=postgres
    - DATABASE_URL=postgresql://synapto:${POSTGRES_PASSWORD}@postgres:5432/synapto
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - selfhealing-network
```

## 6. Add a route in the API Gateway

In `backend/api-gateway/main.py`, add a proxy route:

```python
MY_SERVICE_URL = os.getenv("MY_SERVICE_URL", "http://my-service:8010")

@app.api_route("/api/v1/my-resource/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_my_service(request: Request, path: str, current_user=Depends(get_current_user)):
    return await proxy_request(request, f"{MY_SERVICE_URL}/api/v1/my-resource/{path}")
```

## 7. Add telemetry (optional but recommended)

```python
from synapto_telemetry import TelemetryEmitter
import redis.asyncio as aioredis

redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
emitter = TelemetryEmitter(service_name="my-service", host=os.getenv("HOSTNAME", "unknown"), redis_client=redis_client)

# In a route handler:
emitter.emit_metric("my_metric", value=1.0, unit="count")
```

## 8. Add to the docs

Add a new page under `docs/for-developers/service-internals/my-service.md` and add it to the `nav` in `mkdocs.yml`.
```

- [ ] **Step 10.3: Write `docs/for-developers/contracts.md`**

```markdown
# Contracts & Protos

Synapto uses two mechanisms to enforce interfaces between components: Pydantic schemas (Python services) and Protocol Buffers (gRPC/Agent Service).

## synapto-contracts

`libs/synapto-contracts` defines the shared Pydantic models used by all AIOps libraries and services. Any type that crosses a library boundary lives here.

Key types:

| Type | Used by | Purpose |
|------|---------|---------|
| `AnomalySignal` | synapto-detector, orchestration-layer | Represents a detected anomaly |
| `IncidentClassification` | synapto-classifier | Classification result with layer, component, confidence |
| `RemediationSafety` | synapto-remediator | Safety gate result |
| `Workflow` / `WorkflowResult` | synapto-remediator, orchestration-layer | Remediation workflow input/output |
| `TelemetrySignal` | synapto-telemetry | Metric/log envelope published to Redis |

## Protocol Buffers (Agent Service)

The Agent Service uses gRPC defined in `backend/proto/`. The `.proto` files define the `AgentBridge` service:

```protobuf
service AgentBridge {
  rpc Connect(stream AgentMessage) returns (stream JobPayload);
}
```

After modifying a `.proto` file, regenerate the Python stubs:

```bash
python -m grpc_tools.protoc \
  -I backend/proto \
  --python_out=backend/agent-service \
  --grpc_python_out=backend/agent-service \
  backend/proto/agent.proto
```

## Contract verification

`verify_contracts.py` at the repo root runs a suite of structural checks to catch schema drift:

```bash
python verify_contracts.py
```

This checks that:
- All `synapto-contracts` types can be imported without errors
- All SDK libraries accept the contract types without type errors
- The gRPC proto stubs match the current `.proto` definitions

Run this before any PR that modifies a shared schema.
```

- [ ] **Step 10.4: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/for-developers/database-schema.md docs/for-developers/adding-a-service.md docs/for-developers/contracts.md
git commit -m "docs(developers): add database schema, adding-a-service, contracts pages"
```

---

## Task 11: Reference Pages

**Files:**
- Write: `docs/reference/api.md`
- Write: `docs/reference/configuration.md`
- Write: `docs/reference/changelog.md`

- [ ] **Step 11.1: Write `docs/reference/api.md`**

```markdown
# API Reference

## Interactive documentation

The API Gateway exposes live, interactive documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
- **Redoc:** `http://localhost:8000/redoc`

These pages are generated automatically from the FastAPI route definitions and are always up to date.

## Authentication

All endpoints except event ingestion and login require a valid JWT access token in the `access_token` HttpOnly cookie. Obtain a token via `POST /api/v1/auth/token`.

```bash
# Log in
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=yourpassword"

# Use the cookie on subsequent requests
curl -b cookies.txt http://localhost:8000/api/v1/incidents
```

## Endpoint groups

| Group | Base path | Service |
|-------|-----------|---------|
| Auth | `/api/v1/auth/` | Auth Service |
| Events (ingestion) | `/api/v1/events` | Integration Layer |
| Incidents | `/api/v1/incidents/` | Orchestration Layer |
| Incident stream (SSE) | `/api/v1/incidents/stream` | API Gateway → Redis |
| Playbooks | `/api/v1/playbooks/` | Knowledge Layer |
| Policies | `/api/v1/policies/` | Knowledge Layer |
| Scripts | `/api/v1/knowledge/scripts/` | Knowledge Layer |
| SOPs | `/api/v1/knowledge/sops/` | Knowledge Layer |
| Topology | `/api/v1/knowledge/topology/` | Knowledge Layer |
| Executions | `/api/v1/executions/` | Execution Engine |
| Analytics | `/api/v1/analytics/` | Learning Engine |
| CI/CD Risk | `/api/v1/cicd/` | Integration Layer |
| Service Health | `/api/v1/health/services` | API Gateway |
| Admin — Users | `/api/v1/admin/users/` | Admin Service |
| Admin — Credentials | `/api/v1/admin/credentials/` | Admin Service |
| Admin — AI Settings | `/api/v1/admin/ai-settings/` | Admin Service |
| Admin — Integrations | `/api/v1/admin/integrations/` | Admin Service |
| Admin — SSO | `/api/v1/admin/sso/` | Admin Service |
| Admin — Licensing | `/api/v1/admin/licensing/` | Admin Service |
```

- [ ] **Step 11.2: Write `docs/reference/configuration.md`**

```markdown
# Configuration Reference

All configuration is supplied via environment variables in `.env` (loaded by Docker Compose). Copy `.env.example` as a starting point.

## Required variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `SECRET_KEY` | API Gateway, Auth Service | Signs and verifies JWTs. Generate: `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | All services | PostgreSQL password |
| `REDIS_PASSWORD` | All services | Redis password |
| `ADMIN_DEFAULT_PASSWORD` | Auth Service | Password for the auto-seeded admin user on first startup |
| `ENCRYPTION_KEY` | Admin Service, Execution Engine, Learning Engine | Fernet key for encrypting credentials and API keys. Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

## Optional variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime in days |
| `MAX_EXECUTION_TIMEOUT` | `300` | Maximum script execution timeout in seconds |
| `MAX_CONCURRENT_EXECUTIONS` | `10` | Maximum parallel script executions |
| `INTERNAL_SERVICE_SECRET` | `""` | Shared secret between Execution Engine and Agent Service. Required for agent-based execution. |
| `ED25519_SIGNING_KEY` | `/certs/ed25519_signing.key` | Path to Ed25519 private key for signing agent jobs |
| `TLS_SERVER_CERT_PATH` | `/certs/server.crt` | gRPC server certificate (Agent Service) |
| `TLS_SERVER_KEY_PATH` | `/certs/server.key` | gRPC server private key (Agent Service) |
| `TLS_CA_CERT_PATH` | `/certs/ca.crt` | CA certificate for agent mTLS |
| `APP_ENV` | `development` | Set to `production` to enforce strict security (mTLS required, insecure fallbacks disabled) |
| `CLOUDFLARE_TOKEN` | `""` | Cloudflare Tunnel token (optional, for remote access without port forwarding) |
| `FORCE_SSO` | `false` | Set to `true` to disable local password login |

## Service URLs (internal)

These are set automatically in Docker Compose and generally do not need to be changed unless you are running services outside Docker.

| Variable | Default |
|----------|---------|
| `INTEGRATION_SERVICE_URL` | `http://integration-layer:8001` |
| `ORCHESTRATION_SERVICE_URL` | `http://orchestration-layer:8002` |
| `KNOWLEDGE_SERVICE_URL` | `http://knowledge-layer:8003` |
| `EXECUTION_SERVICE_URL` | `http://execution-engine:8004` |
| `LEARNING_SERVICE_URL` | `http://learning-engine:8005` |
| `AUTH_SERVICE_URL` | `http://auth-service:8006` |
| `ADMIN_SERVICE_URL` | `http://admin-service:8007` |
| `AGENT_SERVICE_URL` | `http://agent-service:8009` |
| `REDIS_URL` | `redis://:<REDIS_PASSWORD>@redis:6379` |
| `DATABASE_URL` | `postgresql://synapto:<POSTGRES_PASSWORD>@postgres:5432/synapto` |
```

- [ ] **Step 11.3: Write `docs/reference/changelog.md`**

```markdown
# Changelog

## Sprint 2026-04-11 — Documentation Site

- Added MkDocs Material documentation site with audience-first navigation (For Operators / For Developers / Reference).

## Sprint 2026-04-10 — UI Features

- **CI/CD Risk Assessment page** (`/cicd`) — live risk scoring form with debounced API calls.
- **Action Catalogue page** (`/catalogue`) — filterable table of gold-standard scripts with Monaco viewer drawer.
- **Service Health widget** — sparkline response time charts on the Dashboard.
- **Real-time incident stream** — replaced 5-second polling with SSE (`GET /api/v1/incidents/stream`).
- **Promotion banner** on Incident detail panel for AI-resolved incidents.
- Added `CI/CD Risk` and `Action Catalogue` sidebar nav items.

## Sprint 2026-04-09 — AIOps Platform v2

- `synapto-sdk` meta-package aggregating all AIOps libraries.
- `synapto-telemetry` instrumented across all 7 backend services.
- `synapto-cicd` library with `CICDRiskScorer`.
- CI/CD risk assessment endpoint via Integration Layer.
- Script promotion flow: `POST /api/v1/incidents/{id}/promote`.

## Sprint 2026-04-08 — Analytics & Events UI

- Analytics bento dashboard with success rate, MTTR, incident counts.
- Events and Executions container-free redesign.
- Playbooks & SOPs bento redesign.

## Sprint 2026-04-07 — UI Redesign

- Dashboard editorial bento layout.
- Incidents container-free redesign.
- Sidebar icon-rail navigation.

## Earlier

See `git log --oneline` for the full commit history.
```

- [ ] **Step 11.4: Verify build and commit**

```bash
mkdocs build --strict 2>&1
git add docs/reference/api.md docs/reference/configuration.md docs/reference/changelog.md
git commit -m "docs(reference): add api reference, configuration, and changelog pages"
```

---

## Task 12: Final Verification & Cleanup

- [ ] **Step 12.1: Full build with strict mode**

```bash
mkdocs build --strict 2>&1
```

Expected output ends with: `INFO - Documentation built in X.X seconds` and no warnings.

- [ ] **Step 12.2: Spot-check the site locally**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000` and verify:
- The three tab groups appear (For Operators / For Developers / Reference)
- Navigation expands correctly in each section
- Code blocks have copy buttons
- No 404 pages in the nav

Press `Ctrl+C` to stop the server.

- [ ] **Step 12.3: Remove the old flat doc files**

The new pages supersede these files. Remove them to avoid confusion:

```bash
git rm docs/architecture/system_design.md
git rm docs/manual/platform_how_to.md
git rm docs/frontend-improvement-plan.md
```

Do not remove `docs/manual/images/` — the architecture diagram is still referenced in `docs/for-developers/architecture-overview.md` and `docs/index.md`.

- [ ] **Step 12.4: Final build to confirm nothing broke**

```bash
mkdocs build --strict 2>&1
```

Expected: clean build, no errors.

- [ ] **Step 12.5: Final commit**

```bash
git add -A
git commit -m "docs: complete MkDocs site — remove superseded flat docs"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|-----------------|-----------|
| MkDocs Material with `navigation.tabs` | Task 1 (mkdocs.yml) |
| For Operators — 12 pages | Tasks 2–5 |
| For Developers — getting-started, architecture | Task 6 |
| For Developers — 10 service internals pages | Tasks 7–8 |
| For Developers — 6 SDK pages | Task 9 |
| For Developers — database-schema, adding-a-service, contracts | Task 10 |
| Reference — api, configuration, changelog | Task 11 |
| Source migration (old files removed after clean build) | Task 12 |
| New content for CI/CD Risk, Action Catalogue, SSE, Agent Service | Tasks 4–5, 8 |
| Content standards (operator: task-based; developer: reference+explanation) | All tasks |

No gaps found.

**Placeholder scan:** No TBDs, TODOs, or vague instructions. Every step includes the complete file content to write.

**Type consistency:** No cross-task type references — each page is standalone markdown.

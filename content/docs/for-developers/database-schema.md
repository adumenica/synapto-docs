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

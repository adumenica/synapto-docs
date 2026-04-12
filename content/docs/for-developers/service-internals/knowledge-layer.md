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

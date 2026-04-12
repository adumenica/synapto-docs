# Playbooks and Policies

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

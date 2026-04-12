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

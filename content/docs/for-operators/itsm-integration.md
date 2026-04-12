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

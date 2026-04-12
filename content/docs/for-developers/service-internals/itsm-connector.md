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

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

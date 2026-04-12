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

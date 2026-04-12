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

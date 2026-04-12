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

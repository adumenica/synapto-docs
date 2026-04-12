# API Reference

## Interactive documentation

The API Gateway exposes live, interactive documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
- **Redoc:** `http://localhost:8000/redoc`

These pages are generated automatically from the FastAPI route definitions and are always up to date.

## Authentication

All endpoints except event ingestion and login require a valid JWT access token in the `access_token` HttpOnly cookie. Obtain a token via `POST /api/v1/auth/token`.

```bash
# Log in
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=yourpassword"

# Use the cookie on subsequent requests
curl -b cookies.txt http://localhost:8000/api/v1/incidents
```

## Endpoint groups

| Group | Base path | Service |
|-------|-----------|---------|
| Auth | `/api/v1/auth/` | Auth Service |
| Events (ingestion) | `/api/v1/events` | Integration Layer |
| Incidents | `/api/v1/incidents/` | Orchestration Layer |
| Incident stream (SSE) | `/api/v1/incidents/stream` | API Gateway → Redis |
| Playbooks | `/api/v1/playbooks/` | Knowledge Layer |
| Policies | `/api/v1/policies/` | Knowledge Layer |
| Scripts | `/api/v1/knowledge/scripts/` | Knowledge Layer |
| SOPs | `/api/v1/knowledge/sops/` | Knowledge Layer |
| Topology | `/api/v1/knowledge/topology/` | Knowledge Layer |
| Executions | `/api/v1/executions/` | Execution Engine |
| Analytics | `/api/v1/analytics/` | Learning Engine |
| CI/CD Risk | `/api/v1/cicd/` | Integration Layer |
| Service Health | `/api/v1/health/services` | API Gateway |
| Admin — Users | `/api/v1/admin/users/` | Admin Service |
| Admin — Credentials | `/api/v1/admin/credentials/` | Admin Service |
| Admin — AI Settings | `/api/v1/admin/ai-settings/` | Admin Service |
| Admin — Integrations | `/api/v1/admin/integrations/` | Admin Service |
| Admin — SSO | `/api/v1/admin/sso/` | Admin Service |
| Admin — Licensing | `/api/v1/admin/licensing/` | Admin Service |

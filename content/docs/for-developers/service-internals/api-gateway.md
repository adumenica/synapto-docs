# API Gateway

**File:** `backend/api-gateway/main.py`  
**Port:** 8000 (the only publicly exposed backend port)

The API Gateway is the single entry point for all client requests — from the browser and from external monitoring systems. It contains no business logic; it is a routing, authentication, and rate-limiting proxy.

## Responsibilities

- **Authentication** — validates the JWT access token (HttpOnly cookie `access_token`) on every protected route via `get_current_user()`. Unauthenticated requests receive a 401.
- **Role-based access** — `require_operator` and `require_admin` decorators enforce role checks per endpoint.
- **Service routing** — uses `httpx` to forward requests to the appropriate backend service. Backend URLs are read from environment variables.
- **Rate limiting** — `slowapi` caps login attempts at 5/min per IP.
- **CORS** — allows the frontend origin (from `CORS_ORIGINS` env var).
- **Retry logic** — `tenacity` exponential backoff (3 attempts, 1–32 s) on outgoing calls.
- **API docs** — Swagger at `/docs`, Redoc at `/redoc`.
- **SSE stream** — `GET /api/v1/incidents/stream` reads from the Redis `events` stream and pushes `text/event-stream` to connected browsers.

## Design note

JWT validation is centralised here in `backend/shared/auth.py`. Backend microservices trust requests forwarded by the Gateway and do not re-validate tokens, keeping security logic in one place.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Signs and verifies JWTs |
| `CORS_ORIGINS` | Comma-separated list of allowed origins |
| `INTEGRATION_SERVICE_URL` | URL of the Integration Layer |
| `ORCHESTRATION_SERVICE_URL` | URL of the Orchestration Layer |
| `KNOWLEDGE_SERVICE_URL` | URL of the Knowledge Layer |
| `EXECUTION_SERVICE_URL` | URL of the Execution Engine |
| `LEARNING_SERVICE_URL` | URL of the Learning Engine |
| `AUTH_SERVICE_URL` | URL of the Auth Service |
| `ADMIN_SERVICE_URL` | URL of the Admin Service |
| `REDIS_URL` | Redis connection string (for SSE stream) |

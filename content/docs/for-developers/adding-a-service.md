# Adding a Service

All Synapto backend services follow the same pattern. This page walks through adding a new FastAPI microservice.

## 1. Create the service directory

```bash
mkdir backend/my-service
touch backend/my-service/main.py
touch backend/my-service/requirements.txt
touch backend/my-service/Dockerfile
```

## 2. Write `main.py`

Follow this template — all existing services use this structure:

```python
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db, get_db
from shared.auth import get_current_user

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="My Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}
```

## 3. Write `requirements.txt`

At minimum:

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
```

Add `synapto-telemetry` if you want to emit metrics to the Service Health dashboard.

## 4. Write the `Dockerfile`

Copy the pattern from any existing service (e.g. `backend/knowledge-layer/Dockerfile`):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../shared /app/shared
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
```

## 5. Add to `docker-compose.yml`

```yaml
my-service:
  build:
    context: ./backend/my-service
    dockerfile: Dockerfile
  container_name: selfhealing-my-service
  environment:
    - SERVICE_NAME=my-service
    - POSTGRES_HOST=postgres
    - DATABASE_URL=postgresql://synapto:${POSTGRES_PASSWORD}@postgres:5432/synapto
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - selfhealing-network
```

## 6. Add a route in the API Gateway

In `backend/api-gateway/main.py`, add a proxy route:

```python
MY_SERVICE_URL = os.getenv("MY_SERVICE_URL", "http://my-service:8010")

@app.api_route("/api/v1/my-resource/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_my_service(request: Request, path: str, current_user=Depends(get_current_user)):
    return await proxy_request(request, f"{MY_SERVICE_URL}/api/v1/my-resource/{path}")
```

## 7. Add telemetry (optional but recommended)

```python
from synapto_telemetry import TelemetryEmitter
import redis.asyncio as aioredis

redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
emitter = TelemetryEmitter(service_name="my-service", host=os.getenv("HOSTNAME", "unknown"), redis_client=redis_client)

# In a route handler:
emitter.emit_metric("my_metric", value=1.0, unit="count")
```

## 8. Add to the docs

Add a new page under `docs/for-developers/service-internals/my-service.md` and add it to the `nav` in `mkdocs.yml`.

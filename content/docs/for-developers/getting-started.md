# Getting Started

## Prerequisites

- Python 3.11+
- Docker and Docker Compose v2+
- Node.js 18+ (for frontend)

## Running services locally

All services are Python FastAPI applications. The recommended dev workflow is:

1. Start infrastructure (Postgres + Redis) in Docker.
2. Run the specific service you're working on locally.
3. Let everything else run in Docker.

```bash
# Start only infrastructure
docker compose up -d postgres redis

# Set up a virtualenv for the service you're editing
cd backend/<service-name>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set env vars (copy from docker-compose.yml for that service)
export DATABASE_URL=postgresql://synapto:changeme@localhost:5432/synapto
export REDIS_URL=redis://:changeme-redis-password@localhost:6379
export SECRET_KEY=dev-secret-key

# Run the service
uvicorn main:app --reload --port <service-port>
```

## Running the frontend locally

```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:5173
```

The frontend Vite dev server proxies API requests to `http://localhost:8000` (the API Gateway). Make sure the API Gateway is running.

## Running all services in Docker (full stack)

```bash
docker compose up -d --build
```

## Installing the Python libraries

The AIOps libraries in `libs/` are pip-installable in editable mode:

```bash
pip install -e libs/synapto-contracts
pip install -e libs/synapto-telemetry
pip install -e libs/synapto-cicd
# etc.
```

Or install the meta-package (pulls in all libs):

```bash
pip install -e libs/synapto-sdk
```

## Shared module

`backend/shared/` contains code used by all Python services: database setup, auth helpers, Redis utilities, Pydantic schemas. It is installed into each service's Docker image automatically (it's mounted as a volume in development).

## Running tests

Each library in `libs/` has a `tests/` directory:

```bash
cd libs/synapto-cicd
pytest tests/ -v
```

Backend services do not currently have unit test suites — integration testing is done by running the full stack and posting events to the API.

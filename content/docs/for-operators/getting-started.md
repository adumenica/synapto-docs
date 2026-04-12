# Getting Started

Synapto runs entirely in Docker. You need Docker, Docker Compose v2+, and a `.env` file. No other dependencies.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2+
- Git
- A terminal with `bash` or `zsh`

## 1. Clone the repository

```bash
git clone https://github.com/adumenica/Synapto.git
cd Synapto
```

## 2. Create the environment file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

| Variable | What to set |
|----------|-------------|
| `SECRET_KEY` | A random 64-character string. Generate with `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | A strong database password |
| `REDIS_PASSWORD` | A strong Redis password |
| `ADMIN_DEFAULT_PASSWORD` | The password for the initial admin user |
| `ENCRYPTION_KEY` | A 32-byte Fernet key. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

See [Configuration Reference](../reference/configuration.md) for the full variable list.

## 3. Start all services

```bash
docker compose up -d --build
```

The first build takes 3–5 minutes while Docker pulls base images and installs Python dependencies.

## 4. Verify all services are healthy

```bash
docker compose ps
```

All containers should show `healthy` or `running`. If a service shows `unhealthy`, check its logs:

```bash
docker compose logs <service-name> --tail 50
```

## 5. Access the platform

| Interface | URL |
|-----------|-----|
| Web UI | `http://localhost:3000` |
| API (Swagger) | `http://localhost:8000/docs` |

Log in with the credentials from [Default Credentials](default-credentials.md).

## Updating

To pull the latest code and rebuild:

```bash
git pull
docker compose up -d --build
```

Database migrations run automatically on startup — no manual steps needed.

!!! tip "Troubleshooting"
    If the frontend shows a blank page, run `docker compose logs selfhealing-frontend --tail 20`. A "cannot find module" error usually means the node_modules cache is stale — run `docker compose build --no-cache frontend`.

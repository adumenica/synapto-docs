# Configuration

All configuration is supplied via environment variables in `.env` (loaded by Docker Compose). Copy `.env.example` as a starting point.

## Required variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `SECRET_KEY` | API Gateway, Auth Service | Signs and verifies JWTs. Generate: `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | All services | PostgreSQL password |
| `REDIS_PASSWORD` | All services | Redis password |
| `ADMIN_DEFAULT_PASSWORD` | Auth Service | Password for the auto-seeded admin user on first startup |
| `ENCRYPTION_KEY` | Admin Service, Execution Engine, Learning Engine | Fernet key for encrypting credentials and API keys. Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

## Optional variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime in days |
| `MAX_EXECUTION_TIMEOUT` | `300` | Maximum script execution timeout in seconds |
| `MAX_CONCURRENT_EXECUTIONS` | `10` | Maximum parallel script executions |
| `INTERNAL_SERVICE_SECRET` | `""` | Shared secret between Execution Engine and Agent Service. Required for agent-based execution. |
| `ED25519_SIGNING_KEY` | `/certs/ed25519_signing.key` | Path to Ed25519 private key for signing agent jobs |
| `TLS_SERVER_CERT_PATH` | `/certs/server.crt` | gRPC server certificate (Agent Service) |
| `TLS_SERVER_KEY_PATH` | `/certs/server.key` | gRPC server private key (Agent Service) |
| `TLS_CA_CERT_PATH` | `/certs/ca.crt` | CA certificate for agent mTLS |
| `APP_ENV` | `development` | Set to `production` to enforce strict security (mTLS required, insecure fallbacks disabled) |
| `CLOUDFLARE_TOKEN` | `""` | Cloudflare Tunnel token (optional, for remote access without port forwarding) |
| `FORCE_SSO` | `false` | Set to `true` to disable local password login |

## Service URLs (internal)

These are set automatically in Docker Compose and generally do not need to be changed unless you are running services outside Docker.

| Variable | Default |
|----------|---------|
| `INTEGRATION_SERVICE_URL` | `http://integration-layer:8001` |
| `ORCHESTRATION_SERVICE_URL` | `http://orchestration-layer:8002` |
| `KNOWLEDGE_SERVICE_URL` | `http://knowledge-layer:8003` |
| `EXECUTION_SERVICE_URL` | `http://execution-engine:8004` |
| `LEARNING_SERVICE_URL` | `http://learning-engine:8005` |
| `AUTH_SERVICE_URL` | `http://auth-service:8006` |
| `ADMIN_SERVICE_URL` | `http://admin-service:8007` |
| `AGENT_SERVICE_URL` | `http://agent-service:8009` |
| `REDIS_URL` | `redis://:<REDIS_PASSWORD>@redis:6379` |
| `DATABASE_URL` | `postgresql://synapto:<POSTGRES_PASSWORD>@postgres:5432/synapto` |

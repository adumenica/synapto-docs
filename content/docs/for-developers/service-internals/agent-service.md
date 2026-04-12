# Agent Service

**Files:** `backend/agent-service/main.py`, `servicer.py`, `auth_interceptor.py`, `enrollment.py`, `signing.py`  
**Port:** 50051 (gRPC) + 8009 (FastAPI internal)

The Agent Service is the bridge between the platform and remotely deployed Synapto agents running on managed nodes. It uses gRPC with mutual TLS (mTLS) — zero-trust: both client and server must present valid certificates.

## Why agents?

When SSH/WinRM is not feasible (firewalls, network segmentation), you can deploy a lightweight Synapto agent on the managed node. The agent connects outbound to port 50051, registers itself, and receives execution jobs via a persistent gRPC stream.

## Security model

- The Agent Service loads a CA certificate, server certificate/key, and an Ed25519 signing key from `/certs/` at startup.
- Every agent must present a certificate signed by the same CA.
- Every job dispatched to an agent is signed with the Ed25519 private key. The agent verifies the signature before executing — this prevents an attacker who intercepts the gRPC stream from injecting fake jobs.
- Agent identity is encoded as a SPIFFE URI: `spiffe://synapto.io/tenant/{tenant_id}/agent/{agent_id}`.

## Enrollment flow

1. Admin generates a one-time enrollment token via the Admin panel.
2. The agent is started on the managed node with the token and the CA certificate.
3. The agent connects to port 50051, presents the token, receives its signed client certificate.
4. The token is consumed and cannot be reused.

## Job dispatch flow

When the Execution Engine routes a job to an agent:

1. Execution Engine calls `POST /dispatch` on the Agent Service's FastAPI interface (internal, protected by `X-Internal-Secret` header).
2. Agent Service validates the target agent exists and is not revoked.
3. Signs the job payload with the Ed25519 private key.
4. Persists the job to the `execution_jobs` table.
5. Pushes the job ID to the Redis Stream `agent-jobs:{agent_id}`.
6. The `AgentBridgeServicer` reads from that stream and delivers the job to the connected agent via its gRPC stream.

## Development mode

If TLS certs are not present and `APP_ENV != production`, the gRPC server starts without mTLS (insecure mode) with a warning. In production, missing certs are fatal.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `INTERNAL_SERVICE_SECRET` | Shared secret for the `/dispatch` endpoint |
| `ED25519_SIGNING_KEY` | Path to the Ed25519 private key (default: `/certs/ed25519_signing.key`) |
| `TLS_SERVER_CERT_PATH` | gRPC server certificate |
| `TLS_SERVER_KEY_PATH` | gRPC server private key |
| `TLS_CA_CERT_PATH` | CA certificate for verifying agent certs |

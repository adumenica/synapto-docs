# Execution Engine

**File:** `backend/execution-engine/main.py`  
**Port:** 8004

The Execution Engine is the "hands" — it safely runs scripts on target infrastructure. All execution is asynchronous: the caller receives an execution ID immediately and polls for the result.

## Supported execution methods

| Method | Target | Library |
|--------|--------|---------|
| SSH | Linux/Unix hosts | `paramiko` |
| WinRM | Windows hosts | `pywinrm` (NTLM auth) |
| Netmiko | Network devices (Cisco, Juniper, etc.) | `netmiko` |
| SQL | Databases | `pymssql` / `pymysql` |
| Docker | Local sandboxed execution | Docker SDK |

## Execution flow

1. Receive `POST /execute` with script content, language, and target host.
2. Look up credentials for the target host from the encrypted credential vault.
3. Mark execution as `RUNNING` in the database.
4. Execute the script (SSH, or Docker container for local/sandbox runs).
5. Capture stdout, stderr, exit code, and timing.
6. Write results to the `executions` table.

## Supported script languages

`PYTHON`, `BASH`, `POWERSHELL`, `SHELL`

## Docker images for sandboxed execution

| Language | Image |
|----------|-------|
| Python | `python:3.11-alpine` |
| PowerShell | `mcr.microsoft.com/powershell:lts-alpine-3.14` |
| Bash/Shell | `alpine:latest` |

## Security hardening

The Execution Engine container runs with:
- Read-only root filesystem
- All Linux capabilities dropped except `DAC_OVERRIDE`
- No new privileges flag
- 100 MB tmpfs at `/tmp` for script staging

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Fernet key for decrypting credentials |
| `AGENT_SERVICE_URL` | Agent Service URL (for agent-based execution) |
| `INTERNAL_SERVICE_SECRET` | Shared secret for Agent Service internal calls |

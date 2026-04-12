# Credential Vault

The Credential Vault stores the credentials the Execution Engine uses to connect to target infrastructure. All credentials are encrypted at rest using a Fernet key (`ENCRYPTION_KEY` in `.env`).

## Supported credential types

| Type | Used for |
|------|---------|
| SSH | Linux/Unix hosts via `paramiko` |
| WinRM | Windows hosts via `pywinrm` (NTLM auth) |
| Netmiko | Network devices (Cisco, Juniper, Arista, etc.) |
| SQL | Databases (MSSQL via `pymssql`, MySQL via `pymysql`) |

## Adding a credential

1. Navigate to **Admin → Credentials**.
2. Click **New Credential**.
3. Select the type, enter the hostname (or IP), username, and password (or SSH key for SSH type).
4. Click **Save**.

The credential is encrypted before being written to the database. The plaintext is never logged.

## How credentials are resolved

When the Execution Engine receives a job, it looks up the credential for the target host using this priority:

1. Exact hostname match
2. Wildcard match (e.g., a credential for `web-*` matches `web-01`)
3. Default credential for the credential type

If no match is found, the execution fails with a `CREDENTIAL_NOT_FOUND` error.

## Rotating a credential

Edit the credential in **Admin → Credentials** and enter the new password. Existing running executions are not affected — they use the credential value that was resolved at the time the job started.

!!! tip "Troubleshooting"
    If executions fail with `Authentication failed`, verify the credential hostname matches the `target_host` value shown in the Execution detail. Check the Execution Engine logs: `docker compose logs selfhealing-execution --tail 30`.

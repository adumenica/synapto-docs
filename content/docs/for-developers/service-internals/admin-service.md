# Admin Service

**File:** `backend/admin-service/main.py`  
**Port:** 8007

Provides the administrative control plane for the platform.

## Capabilities

| Area | What it manages |
|------|----------------|
| **Users** | Create, update, deactivate users; assign roles |
| **Credentials** | Encrypted vault for SSH, WinRM, Netmiko, SQL credentials |
| **AI Settings** | AI provider selection, encrypted API key storage |
| **ITSM Integrations** | ServiceNow, Jira, BMC Remedy connection config |
| **SSO / External Identity** | OIDC provider configuration (Azure AD, Okta, Keycloak, etc.) |
| **Licensing** | Subscription tier management, usage tracking, on-premise key validation |
| **Audit Logs** | Immutable record of all admin actions (who, what, when, from where) |
| **System Settings** | Global parameters (max execution timeout, max concurrent executions) |

## Encryption

Credentials and AI API keys are encrypted at rest using a Fernet symmetric key (`ENCRYPTION_KEY`). The plaintext is never logged and never stored in plaintext.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Fernet key for encrypting credentials and API keys |

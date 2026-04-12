# Default Credentials

On first startup, Synapto creates one admin user automatically if `ADMIN_DEFAULT_PASSWORD` is set in `.env`.

## Default admin account

| Field | Value |
|-------|-------|
| Username | `admin` |
| Role | `admin` |
| Password | Value of `ADMIN_DEFAULT_PASSWORD` in your `.env` |

!!! warning "Change this immediately"
    Log in and change the admin password before exposing the platform to a network. The default account has full admin privileges.

## How to change the password

1. Log in to the Web UI at `http://localhost:3000`.
2. Click your username in the top-right corner → **Profile**.
3. Enter your current password and the new password, then click **Save**.

Or via API:

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/admin \
  -H "Content-Type: application/json" \
  --cookie "access_token=<your_token>" \
  -d '{"password": "your-new-secure-password"}'
```

## Creating additional users

Operators and admins can create users in the Admin panel:

1. Navigate to **Admin → Users**.
2. Click **New User**.
3. Set username, password, and role (`viewer`, `operator`, or `admin`).

## Roles

| Role | Capabilities |
|------|-------------|
| `viewer` | Read-only access to incidents, events, executions, and analytics |
| `operator` | All viewer capabilities plus: approve remediations, trigger executions, manage playbooks |
| `admin` | All operator capabilities plus: manage users, credentials, AI settings, ITSM, SSO, licensing |

!!! tip "Troubleshooting"
    If no admin user was created on first startup, check that `ADMIN_DEFAULT_PASSWORD` is set in `.env` and that the `auth-service` container started without errors (`docker compose logs selfhealing-auth --tail 30`).

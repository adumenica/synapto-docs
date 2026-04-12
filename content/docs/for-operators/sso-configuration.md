# SSO Configuration

Synapto supports Single Sign-On via OIDC (OpenID Connect). Once configured, users can log in with their organisation's identity provider instead of a local password.

## Supported providers

Any OIDC-compliant provider, including:
- Microsoft Entra ID (Azure AD)
- Okta
- Google Workspace
- Keycloak
- Auth0

## Setting up OIDC

1. In your identity provider, create a new **OIDC application** (or OAuth2 app):
   - **Redirect URI:** `http://<synapto-host>:8000/auth/callback`
   - **Scopes:** `openid email profile`
   - Note the **Client ID** and **Client Secret**.

2. In Synapto, navigate to **Admin → SSO**.
3. Fill in the OIDC details:

   | Field | Description |
   |-------|-------------|
   | Provider Name | Display name shown on the login button |
   | Client ID | From your identity provider |
   | Client Secret | From your identity provider |
   | Discovery URL | The OIDC discovery endpoint, e.g. `https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration` |
   | Default Role | Role assigned to new users on first login (`viewer` recommended) |

4. Click **Save**. A **Sign in with [Provider]** button appears on the login page.

## User provisioning

On first SSO login, Synapto creates a local user account with the email from the OIDC token. The default role is set to whatever you configured. Admins can change individual user roles in **Admin → Users** after provisioning.

## Disabling local login

If you want to enforce SSO-only login, set `FORCE_SSO=true` in `.env` and restart the Auth Service. Local password authentication will be disabled — ensure your SSO connection is working before doing this.

!!! tip "Troubleshooting"
    If login redirects back to the login page with no error, check the Auth Service logs for OIDC callback errors: `docker compose logs selfhealing-auth --tail 30`. The most common cause is a mismatched redirect URI — verify it matches exactly, including the trailing slash (or lack thereof).

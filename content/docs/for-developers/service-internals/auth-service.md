# Auth Service

**File:** `backend/auth-service/main.py`  
**Port:** 8006

Handles all authentication and session management.

## Login flow

1. Client POSTs credentials to `POST /token` (OAuth2 password flow, `application/x-www-form-urlencoded`).
2. Auth Service validates credentials against the Argon2id-hashed password in `users`.
3. If valid: generates an access token (60 min) and refresh token (7 days) as JWTs.
4. **Both tokens are returned as HttpOnly cookies** (`access_token`, `refresh_token`), not in the response body — JavaScript cannot read them, preventing XSS-based token theft.
5. Token hashes are stored in `oauth_tokens` — allows revocation without a blocklist.

## Other endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /refresh` | Validates refresh token cookie, issues new access token |
| `POST /logout` | Clears both cookies server-side |
| `GET /me` | Returns the current user's profile |

## Default user seeding

On first startup, if no admin user exists and `ADMIN_DEFAULT_PASSWORD` is set, a default admin user is created.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Signs JWTs (must match the value used by the API Gateway) |
| `ADMIN_DEFAULT_PASSWORD` | Password for the seeded admin user |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (default: 60) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (default: 7) |

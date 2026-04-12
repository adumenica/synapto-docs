# Learning Engine

**File:** `backend/learning-engine/main.py`  
**Port:** 8005

The Learning Engine provides all AI-driven capabilities and platform analytics.

## AI endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /analyze` | Analyses an incident and predicts root cause |
| `POST /generate-diagnostic` | Generates a new SOP + diagnostic playbook from an incident description |
| `POST /generate-composite-script` | Merges multiple playbook steps into a single unified script |
| `GET /analytics` | Returns success rates, MTTR, incident counts, top incident types |
| `GET /recommendations` | Suggests improvements based on historical data |

## Supported AI providers

| Provider | Model |
|----------|-------|
| Anthropic Claude (primary) | `claude-3-5-sonnet-20241022` |
| OpenAI | GPT-4o |
| Google | Gemini 1.5 Pro |

The active provider and API key are configured via the Admin panel and stored encrypted in `ai_settings`.

## The learning loop

1. Execution Engine successfully runs an AI-generated script.
2. Orchestration Layer calls `POST /incidents/{id}/promote`.
3. Learning Engine sets `is_gold_standard=true` on the SOP.
4. On the next similar incident, Orchestration Layer's Tier 2 finds the SOP and skips AI generation — saving time and cost.

## Key env vars

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ENCRYPTION_KEY` | For decrypting AI API keys stored in the DB |

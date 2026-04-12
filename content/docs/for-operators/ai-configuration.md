# AI Configuration

Synapto uses AI for Tier 3 playbook generation, incident analysis, and script learning. You configure the AI provider and API key from the Admin panel.

## Supported providers

| Provider | Model used |
|----------|-----------|
| Anthropic Claude | `claude-3-5-sonnet-20241022` |
| OpenAI | GPT-4o |
| Google | Gemini 1.5 Pro |

## Setting up the AI provider

1. Navigate to **Admin → AI Settings**.
2. Select your provider.
3. Enter your API key.
4. Click **Save**.

The API key is encrypted using your `ENCRYPTION_KEY` before being stored in the database.

## Testing the connection

After saving, click **Test Connection**. Synapto sends a minimal prompt to the provider and reports success or the error returned.

## How AI is used

| Feature | Trigger |
|---------|---------|
| Incident analysis | Tier 3 only — when no playbook or SOP matches |
| SOP generation | Alongside incident analysis — the generated SOP is saved for future reuse |
| Composite script generation | Merges multiple playbook steps into a single script to reduce SSH connections |
| Analytics recommendations | Background job that analyses historical incident data |

## Cost management

Synapto calls AI only on Tier 3 misses. If your SOP library covers common incidents well, AI usage is low. The Admin panel shows a usage counter for AI calls in the current billing period.

!!! tip "Troubleshooting"
    If AI generation fails with a 502 error on the Learning Engine, check the Learning Engine logs: `docker compose logs selfhealing-learning --tail 30`. A `401 Unauthorized` from the AI provider means the API key is wrong. A `429 Too Many Requests` means your provider rate limit is exhausted.

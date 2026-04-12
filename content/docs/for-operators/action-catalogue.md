# Action Catalogue

The **Action Catalogue** (`/catalogue`) is the curated library of proven remediation scripts. Every script here has been either human-authored or AI-generated and then promoted by an operator — it is safe to reuse without AI involvement.

## Browsing the catalogue

The catalogue shows a filterable table with columns: Name, Category, Language, Promoted (date), and Actions.

Filter by:
- **Search** — matches script name
- **Category** — `diagnostic`, `remediation`, `cleanup`, `monitoring`
- **Language** — `Python`, `Bash`, `PowerShell`, `Shell`

Click any row to open the script drawer. The drawer shows:
- Script metadata (category, language, promoted date)
- Full script content in a read-only code editor
- A link to the source incident that produced the script

## Promoting an AI fix to the catalogue

When the Learning Engine generates a fix that successfully resolves an incident, a promotion banner appears at the top of the Incident detail panel:

> "This incident was resolved by AI. Promote the fix to the Action Catalogue?"

Click **Promote to Catalogue** to mark the script as `is_gold_standard = true`. It will then appear in the catalogue and be preferred by the Orchestration Layer's Tier 2 matching on future incidents with similar titles.

## Removing a script from the catalogue

Open the script drawer and click **Remove from Catalogue**. This sets `is_gold_standard = false` — the script is not deleted, just demoted. It can be re-promoted later.

!!! tip "Troubleshooting"
    If the promotion banner does not appear on a resolved incident, check that `incident.meta_data.promotion_eligible` is `true`. This flag is set by the Learning Engine when it generates the fix. If it is missing, confirm the incident was resolved by Tier 3 (AI) and not Tier 1 or 2 — Tier 1/2 resolutions use existing scripts and are not promotion candidates.

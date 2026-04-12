# CI/CD Risk Assessment

The **CI/CD Risk** page (`/cicd`) scores a planned deployment for risk before you run it. Fill in the deployment details and the risk score updates live as you type — no submit button needed.

## Risk factors

The scorer weights these factors:

| Factor | Max contribution |
|--------|-----------------|
| Production environment | +0.30 |
| Database migration | +0.30 |
| Large changeset (>30 files) | +0.20 |
| Off-hours deployment | +0.15 |
| No rollback available | +0.15 |
| >2 affected services | +0.10 |

Scores are capped at 1.0. The risk levels are:

| Score | Level | Recommendation |
|-------|-------|----------------|
| 0.0–0.29 | Low | Deploy with standard monitoring |
| 0.30–0.59 | Medium | Deploy during business hours with enhanced monitoring |
| 0.60–0.79 | High | Requires manual approval and rollback plan |
| 0.80–1.0 | Critical | Requires senior engineer approval, staged rollout, and war room |

## Using the page

1. Navigate to **CI/CD Risk** in the sidebar.
2. Fill in the deployment form (left column):
   - **Service name** — the service being deployed
   - **Environment** — development / staging / production
   - **Changed files** — number of files changed in the PR
   - **Affected services** — comma-separated list of downstream services
   - **DB migration** — toggle on if the deployment includes a schema migration
   - **Off-hours** — toggle on if deploying outside business hours
   - **Rollback available** — toggle on if you have a tested rollback procedure (default: on)
   - **Commit message** — optional, for your records
3. The right panel shows the risk score, level badge, contributing factors, and a recommendation.

If the score is ≥ 0.6, a **"Manual approval required"** warning appears.

!!! tip "Troubleshooting"
    If the risk panel stays empty after filling in fields, check the browser network tab for a failed `POST /api/v1/cicd/risk-assessment`. Ensure the API Gateway container is healthy and your session cookie is valid (log out and back in if needed).

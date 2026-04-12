# Changelog

## Sprint 2026-04-11 — Documentation Site

- Added MkDocs Material documentation site with audience-first navigation (For Operators / For Developers / Reference).

## Sprint 2026-04-10 — UI Features

- **CI/CD Risk Assessment page** (`/cicd`) — live risk scoring form with debounced API calls.
- **Action Catalogue page** (`/catalogue`) — filterable table of gold-standard scripts with Monaco viewer drawer.
- **Service Health widget** — sparkline response time charts on the Dashboard.
- **Real-time incident stream** — replaced 5-second polling with SSE (`GET /api/v1/incidents/stream`).
- **Promotion banner** on Incident detail panel for AI-resolved incidents.
- Added `CI/CD Risk` and `Action Catalogue` sidebar nav items.

## Sprint 2026-04-09 — AIOps Platform v2

- `synapto-sdk` meta-package aggregating all AIOps libraries.
- `synapto-telemetry` instrumented across all 7 backend services.
- `synapto-cicd` library with `CICDRiskScorer`.
- CI/CD risk assessment endpoint via Integration Layer.
- Script promotion flow: `POST /api/v1/incidents/{id}/promote`.

## Sprint 2026-04-08 — Analytics & Events UI

- Analytics bento dashboard with success rate, MTTR, incident counts.
- Events and Executions container-free redesign.
- Playbooks & SOPs bento redesign.

## Sprint 2026-04-07 — UI Redesign

- Dashboard editorial bento layout.
- Incidents container-free redesign.
- Sidebar icon-rail navigation.

## Earlier

See `git log --oneline` for the full commit history.

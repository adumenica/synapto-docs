# Documentation Site — Architecture & How-To

**Date:** 2026-04-11
**Status:** Approved

---

## Goal

Restructure Synapto's documentation into a MkDocs Material site with audience-first navigation. Replace the existing flat files (`docs/architecture/system_design.md`, `docs/manual/platform_how_to.md`) with a properly organised docs site that covers all features through the latest development sprint (CI/CD Risk, Action Catalogue, SSE incidents, Service Health widget, synapto-sdk, telemetry instrumentation, Agent Service).

---

## Audience Split

Two primary audiences with distinct needs:

| Audience | Role | Primary questions |
|----------|------|-------------------|
| **Operators / SREs** | Deploy and run Synapto, respond to incidents, configure integrations | How do I set this up? How do I use feature X in the UI? |
| **Developers / Contributors** | Extend Synapto, build on the SDK, add services | How does service X work internally? How do I add a new service? How do I use the Python libs? |

Shared content (API reference, env var configuration) lives in a dedicated "Reference" section.

---

## Site Structure

```
docs/
├── mkdocs.yml
├── index.md
│
├── for-operators/
│   ├── getting-started.md
│   ├── default-credentials.md
│   ├── webhook-integrations.md
│   ├── incident-management.md
│   ├── action-catalogue.md
│   ├── cicd-risk.md
│   ├── service-health.md
│   ├── playbooks-and-policies.md
│   ├── credential-vault.md
│   ├── ai-configuration.md
│   ├── itsm-integration.md
│   └── sso-configuration.md
│
├── for-developers/
│   ├── getting-started.md
│   ├── architecture-overview.md
│   ├── service-internals/
│   │   ├── api-gateway.md
│   │   ├── integration-layer.md
│   │   ├── orchestration-layer.md
│   │   ├── knowledge-layer.md
│   │   ├── execution-engine.md
│   │   ├── learning-engine.md
│   │   ├── auth-service.md
│   │   ├── admin-service.md
│   │   ├── agent-service.md
│   │   └── itsm-connector.md
│   ├── sdk/
│   │   ├── overview.md
│   │   ├── synapto-cicd.md
│   │   ├── synapto-classifier.md
│   │   ├── synapto-detector.md
│   │   ├── synapto-remediator.md
│   │   └── synapto-telemetry.md
│   ├── database-schema.md
│   ├── adding-a-service.md
│   └── contracts.md
│
└── reference/
    ├── api.md
    ├── configuration.md
    └── changelog.md
```

**Total pages:** 31 markdown files + `mkdocs.yml`

---

## MkDocs Configuration

```yaml
site_name: Synapto Docs
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - toc.integrate
    - content.code.copy
  palette:
    - scheme: default
      primary: indigo
plugins:
  - search
  - tags
  - git-revision-date-localized
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.tabbed
  - tables
  - toc:
      permalink: true
nav:
  - Home: index.md
  - For Operators:
      - Getting Started: for-operators/getting-started.md
      - Default Credentials: for-operators/default-credentials.md
      - Webhook Integrations: for-operators/webhook-integrations.md
      - Incident Management: for-operators/incident-management.md
      - Action Catalogue: for-operators/action-catalogue.md
      - CI/CD Risk Assessment: for-operators/cicd-risk.md
      - Service Health: for-operators/service-health.md
      - Playbooks & Policies: for-operators/playbooks-and-policies.md
      - Credential Vault: for-operators/credential-vault.md
      - AI Configuration: for-operators/ai-configuration.md
      - ITSM Integration: for-operators/itsm-integration.md
      - SSO Configuration: for-operators/sso-configuration.md
  - For Developers:
      - Getting Started: for-developers/getting-started.md
      - Architecture Overview: for-developers/architecture-overview.md
      - Service Internals:
          - API Gateway: for-developers/service-internals/api-gateway.md
          - Integration Layer: for-developers/service-internals/integration-layer.md
          - Orchestration Layer: for-developers/service-internals/orchestration-layer.md
          - Knowledge Layer: for-developers/service-internals/knowledge-layer.md
          - Execution Engine: for-developers/service-internals/execution-engine.md
          - Learning Engine: for-developers/service-internals/learning-engine.md
          - Auth Service: for-developers/service-internals/auth-service.md
          - Admin Service: for-developers/service-internals/admin-service.md
          - Agent Service: for-developers/service-internals/agent-service.md
          - ITSM Connector: for-developers/service-internals/itsm-connector.md
      - SDK:
          - Overview: for-developers/sdk/overview.md
          - synapto-cicd: for-developers/sdk/synapto-cicd.md
          - synapto-classifier: for-developers/sdk/synapto-classifier.md
          - synapto-detector: for-developers/sdk/synapto-detector.md
          - synapto-remediator: for-developers/sdk/synapto-remediator.md
          - synapto-telemetry: for-developers/sdk/synapto-telemetry.md
      - Database Schema: for-developers/database-schema.md
      - Adding a Service: for-developers/adding-a-service.md
      - Contracts: for-developers/contracts.md
  - Reference:
      - API Reference: reference/api.md
      - Configuration: reference/configuration.md
      - Changelog: reference/changelog.md
```

---

## Content Standards

### Operator pages

- Open with one sentence: what this feature does and why an operator cares.
- Use numbered steps for setup procedures.
- Use `curl` examples for any API interactions.
- End with an `!!! tip "Troubleshooting"` admonition covering the most common failure mode.
- No internal service details, no Python code.

### Developer pages (service internals)

- Open with the service's single-sentence purpose.
- Cover: key responsibilities, notable design decisions (the "why"), file paths, env vars, and how the service fits into the wider data flow.
- Source content from existing `docs/architecture/system_design.md` — migrate, don't rewrite.
- Add new content for services not previously documented: Agent Service, Admin Service (full), ITSM Connector details.

### SDK pages

- Install snippet first.
- Primary class/function with type signatures.
- Minimal working example.
- Link to the backend service that consumes this lib.

### Reference pages

- `api.md`: links to live Swagger at `http://localhost:8000/docs`, plus a grouped endpoint table.
- `configuration.md`: single table of all env vars from `docker-compose.yml`, with type, default, and description columns.
- `changelog.md`: feature history grouped by sprint, derived from git log.

---

## Source Migration Strategy

| Existing file | Disposition |
|---------------|-------------|
| `docs/architecture/system_design.md` | Split into `for-developers/architecture-overview.md` + individual `service-internals/*.md` pages |
| `docs/manual/platform_how_to.md` | Split into the 12 `for-operators/*.md` pages |
| `README.md` | Keep as-is; `docs/index.md` will be a trimmed version of it |
| `docs/superpowers/specs/` | Stays in place (internal, not part of the docs site nav) |
| `docs/superpowers/plans/` | Stays in place |

Existing files are **not deleted** until the new pages are written and verified. The old files can be removed in a follow-up commit once the site builds cleanly.

---

## New Content Required (not in existing docs)

| Page | Source |
|------|--------|
| `for-operators/action-catalogue.md` | `docs/superpowers/specs/2026-04-10-ui-features-design.md` + code |
| `for-operators/cicd-risk.md` | Same spec + `frontend/src/pages/CICDRisk.tsx` |
| `for-operators/service-health.md` | Same spec + `frontend/src/components/` |
| `for-operators/incident-management.md` | Existing how-to (partial) + SSE hook details |
| `for-developers/service-internals/agent-service.md` | `backend/agent-service/` code |
| `for-developers/sdk/synapto-cicd.md` | `libs/synapto-cicd/` |
| `for-developers/sdk/synapto-telemetry.md` | `libs/synapto-telemetry/` |
| `for-developers/sdk/overview.md` | `libs/synapto-sdk/` |
| `for-developers/adding-a-service.md` | Derived from patterns across existing services |
| `for-developers/contracts.md` | `verify_contracts.py` + `backend/proto/` |
| `reference/configuration.md` | `docker-compose.yml` + service `main.py` env reads |
| `reference/changelog.md` | `git log` |

---

## Out of Scope

- Deploying the MkDocs site to GitHub Pages or a CDN (separate task).
- Auto-generating API reference from OpenAPI spec (separate task).
- Versioned docs (separate task).
- Translating docs into other languages.

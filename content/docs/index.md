# Synapto

**Synapto** is an AI-augmented, self-healing infrastructure platform. When a monitoring tool fires an alert, Synapto automatically ingests it, correlates related events into an incident, finds or generates a remediation playbook, executes the fix on the affected infrastructure, and learns from the outcome.

## Core philosophy — "Library-First, AI-Fallback"

Synapto always tries to resolve an incident using a pre-approved, human-validated SOP script first. AI only steps in when no match exists. Successful AI-generated fixes are automatically promoted into the SOP library for future reuse.

## Where to start

<div class="grid cards" markdown>

-   **For Operators**

    Deploy Synapto, configure integrations, and manage incidents from the UI.

    [Getting Started →](for-operators/getting-started.md)

-   **For Developers**

    Understand the internals, extend services, and use the Python SDK.

    [Architecture Overview →](for-developers/architecture-overview.md)

-   **API Reference**

    Endpoint summary and link to the interactive Swagger UI.

    [Reference →](reference/api.md)

-   **Configuration**

    All environment variables and Docker Compose overrides.

    [Configuration →](reference/configuration.md)

</div>

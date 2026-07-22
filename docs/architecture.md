# Architecture

`architecture/system.mmd` is the source and `portfolio/assets/system.png` is its reviewed rendered asset. The implemented request path is FastAPI → deterministic catalog → SQL validation → read-only local DuckDB → trust verdict. OpenTelemetry request, generation, validation, and execution spans plus structured lifecycle events carry trace ID, latency, and local cost fields; raw questions are not attached to spans or logs.

The future Azure topology is intentionally non-applied in `infra/main.bicep`: Container Apps, PostgreSQL Flexible Server, Key Vault, Application Insights/Log Analytics, private network configuration, and a Foundry-compatible endpoint abstraction. It requires owner approval for subscriptions, networking, identities, secrets, region/SKU costs, retention, and teardown. No Azure resource exists because of this repository.

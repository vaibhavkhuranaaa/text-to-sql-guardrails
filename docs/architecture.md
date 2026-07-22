# Architecture

`architecture/system.mmd` is the source and `portfolio/assets/system.png` is its reviewed rendered asset. The implemented request path is FastAPI analyst console/API → deterministic catalog → SQL validation → read-only local DuckDB → trust verdict. OpenTelemetry request, generation, validation, and execution spans plus structured lifecycle events carry trace ID, latency, and local cost fields; raw questions are not attached to spans or logs.

The data-release path is deliberately separate from request handling: owner approval → checksum-pinned public-source fetch or local checksum verification → row-free schema profile → strict V2 CSV normalization and quality checks → atomic identifier-free DuckDB snapshot + metadata → evaluation and benchmark evidence. The v1 walkthrough always retains its deterministic demo fixture; v2 proposals use the approved snapshot when present. A snapshot is never downloaded, rebuilt, or modified by an analyst request.

The future Azure topology is intentionally non-applied in `infra/main.bicep`: Container Apps, PostgreSQL Flexible Server, Key Vault, Application Insights/Log Analytics, private network configuration, and a Foundry-compatible endpoint abstraction. It requires owner approval for subscriptions, networking, identities, secrets, region/SKU costs, retention, and teardown. No Azure resource exists because of this repository.

# Architecture

`architecture/system.mmd` is the source and `portfolio/assets/system.png` is its reviewed rendered asset. The implemented request path is FastAPI analyst console/API → deterministic catalog → SQL validation → read-only local DuckDB → trust verdict. OpenTelemetry request, generation, validation, and execution spans plus structured lifecycle events carry trace ID, latency, and local cost fields; raw questions are not attached to spans or logs.

The data-release path is deliberately separate from request handling: owner approval → checksum-pinned public-source fetch or local checksum verification → row-free schema profile → strict V2 CSV normalization and quality checks → atomic identifier-free DuckDB snapshot + metadata → evaluation and benchmark evidence. The v1 walkthrough always retains its deterministic demo fixture; v2 proposals use the approved snapshot when present. A snapshot is never downloaded, rebuilt, or modified by an analyst request.

The current temporary deployment was created outside `infra/main.bicep` and is recorded in `evidence/deployment/temporary-demo.json`. It uses one externally reachable Container Apps replica, managed identity for Azure OpenAI, the committed synthetic fixture, and ephemeral SQLite proposal state. The Bicep file remains a non-applied protected-hosting reference; it is not evidence for the current resources.

Source-level anonymous-demo controls bound proposals per hashed client and per process, emit status-only limit events, expose aggregate counters at `/v1/status`, and can refuse requests after an owner-set expiry. The current deployed revision predates those changes, so they are not public deployment claims until a replacement revision is separately authorized and verified.

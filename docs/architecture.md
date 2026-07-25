# Architecture

`architecture/system.mmd` is the source and `portfolio/assets/system.png` is its reviewed rendered asset. The implemented request path is FastAPI analyst console/API → deterministic catalog → SQL validation → read-only local DuckDB → trust verdict. OpenTelemetry request, generation, validation, and execution spans plus structured lifecycle events carry trace ID, latency, and local cost fields; raw questions are not attached to spans or logs.

The data-release path is deliberately separate from request handling: owner approval → checksum-pinned public-source fetch or local checksum verification → row-free schema profile → strict V2 CSV normalization and quality checks → atomic identifier-free DuckDB snapshot + metadata → evaluation and benchmark evidence. The v1 walkthrough always retains its deterministic demo fixture; v2 proposals use the approved snapshot when present. A snapshot is never downloaded, rebuilt, or modified by an analyst request.

The anonymous live deployment was created outside `infra/main.bicep` and is recorded in `evidence/deployment/anonymous-live-demo.json`. It uses one externally reachable Container Apps replica, managed identity for Azure OpenAI, the committed synthetic fixture, and ephemeral SQLite proposal state. The Bicep file remains a non-applied protected-hosting reference; it is not evidence for the current resources.

Source-level anonymous-demo controls bound proposals per hashed client and per process, emit status-only limit events, and expose aggregate counters at `/v1/status`. They do not provide caller authorization, durable distributed limits, or a production availability guarantee.

The M1 proposal telemetry is also process-local: `/v1/status` exposes only
aggregate proposal outcomes, provider-call counts, provider-reported token
totals, and fixed latency buckets. Lifecycle logs are sampled status-only
metadata with identifiers removed and no configured exporter. Both forms reset
on restart or scale-to-zero and retain no raw questions, SQL, result rows,
client identifiers, token values, or trace IDs.

## Planned scale evidence boundary

The next milestone does not alter the live topology by default. The public demo stays at zero-to-one replica with ephemeral SQLite approval state. If the owner authorizes a two-replica or restart-persistence proof, the first durable-store candidate is Azure Table Storage, accessed with the Container App's managed identity. One pending approval is represented by one entity and consumed by an ETag-conditional delete; quota counters use conditional updates and a bounded expiry cleanup path. This is sufficient for short-lived, low-volume state but is not a relational analytics platform.

Azure Database for PostgreSQL is deliberately not the default cost choice. It is reserved for an owner-approved escalation if measured contention, relational operational queries, or long-lived state make Table Storage's optimistic-concurrency model unsuitable. Neither option authorizes a public database endpoint, user login, real data, or an availability claim.

# Technology decisions

- FastAPI: a typed HTTP contract for the local prototype.
- SQLGlot: parser-backed SQL policy enforcement before DuckDB sees a query.
- DuckDB: compact local analytical execution; it remains the public-demo query engine.
- OpenTelemetry API: portable tracing boundary with no exporter or deployment claim.
- Azure Table Storage (proposed, not provisioned): the first durable-state option if owner-approved cross-replica evidence is required. ETag conditional operations suit five-minute approvals and low-volume counters at materially lower standing cost than PostgreSQL.
- Azure Database for PostgreSQL (deferred escalation): appropriate only for owner-approved relational operational state, sustained contention, or richer reporting; not the default for the anonymous scale-to-zero demo.

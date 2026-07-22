# Technology decisions

- FastAPI: a typed HTTP contract for the local prototype.
- SQLGlot: parser-backed SQL policy enforcement before DuckDB sees a query.
- DuckDB: compact local analytical execution; production PostgreSQL is a future target only.
- OpenTelemetry API: portable tracing boundary with no exporter or deployment claim.

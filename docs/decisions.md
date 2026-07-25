# Decisions

- DuckDB is used in-memory for a repeatable local fixture and read-only query demonstration.
- The generator is deterministic and catalog-bound so the evaluation measures guardrail behavior without model-provider variability.
- MoMTSim V2 is referenced for public synthetic-data provenance; this repository redistributes no source rows.
- The anonymous public demo remains a scale-to-zero, one-replica service. Its SQLite approval state and process-local proposal limits are deliberate cost boundaries, not durable-control claims.
- Durable shared approval/quota state is not provisioned by default. If the owner authorizes multi-replica or restart-persistence evidence, evaluate Azure Table Storage first: ETag conditional operations cover one-time approval consumption and low-volume counters without a standing database. PostgreSQL is an escalation option for relational reporting, sustained contention, or longer-lived operational state.
- Any IBM AML benchmark is private, checksum-pinned, ignored by Git and container builds, and used only for controlled evaluation. Raw rows, account-like identifiers, laundering labels, prompts, result rows, tokens, and environment values are never public evidence.

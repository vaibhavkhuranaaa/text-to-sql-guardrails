# Decisions

- DuckDB is used in-memory for a repeatable local fixture and read-only query demonstration.
- The generator is deterministic and catalog-bound so the evaluation measures guardrail behavior without model-provider variability.
- MoMTSim V2 is referenced for public synthetic-data provenance; this repository redistributes no source rows.

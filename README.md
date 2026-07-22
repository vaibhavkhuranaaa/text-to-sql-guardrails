# Text-to-SQL Interface with Guardrails and Hallucination Detection

## Status

Private, local-first prototype. The backwards-compatible v1 walkthrough uses a deliberately small deterministic catalog. The v2 contract adds Azure Foundry natural-language SQL proposals, analyst approval, and policy revalidation; it is not deployed, not a bank system, and not production-ready.

## One analyst workflow

```bash
uv sync --group dev
uv run guardrails "What is the total amount of completed payments?"
uv run guardrails "Delete all payments"
```

The first command returns a `trusted` verdict with generated SQL, validation checks, a result preview, a trace ID, latency, and local cost `$0`. The second returns `refused`: only exact questions from the versioned catalog are supported. Start the API with `uv run uvicorn guardrails.api:app --reload` and open `http://127.0.0.1:8000` for the integrated analyst console. Its status panel distinguishes the committed demo fixture from an approved snapshot.

`POST /v2/query-proposals` is deliberately separate: it sends the question only to an owner-configured Azure Foundry deployment along with the curated semantic catalog and returns a proposed SQL review package. It never executes SQL. `POST /v2/query-proposals/{id}/execute` needs the short-lived approval token returned with that proposal, then rechecks its policy and snapshot checksum before read-only execution. Pending approvals are SQLite-backed, single-use, and expire after five minutes; they retain SQL/review metadata but never the analyst question or result rows. Locally the store defaults to `/tmp/text-to-sql-guardrails-proposals.sqlite3`; a multi-replica deployment must mount a private writable volume and set `GUARDRAILS_PROPOSAL_STORE` to one shared path. V2 needs `AZURE_FOUNDRY_ENDPOINT`, `AZURE_FOUNDRY_DEPLOYMENT`, and Microsoft Entra ID authorization; locally, authenticate with `az login`, and in Azure use a managed identity. API keys are not used or accepted by this adapter.

Docker path: `docker compose up --build`.

## Guardrails

Every candidate query is parsed before execution. The validator permits one bounded read-only statement, including CTEs, joins, subqueries, window functions, and set operations supported by DuckDB. It allows only classified tables/columns, excludes identifier-like fields from projections and model context, blocks file/network functions and DDL/DML, performs `EXPLAIN`, and bounds previews to 100 rows. Each connection is capped at 512MB, two DuckDB threads, no temporary-disk spill, and a three-second interrupting execution budget; no partial result is returned after timeout. Unsupported requests, malformed SQL, unknown tables/columns, identifier projections, and write operations are refused before DuckDB execution.

## Approved data release, evidence, and limitations

The fixture at `data/fixtures/payments.json` is a small hand-authored normalized synthetic demo fixture; it does not contain rows downloaded from the source dataset, real customer data, cardholder data, or bank data. Its schema/domain inspiration is disclosed in `data/PROVENANCE.md`. `data/source_manifest.json` pins the public DOI, version, license, filenames, and owner-verified checksums. `uv run guardrails data build --source <reviewed.csv>` accepts only the observed V2 headers and atomically emits an ignored local DuckDB snapshot containing simulation step, transaction type, amount, balance features, and fraud label. Simulation step, type, amount, and fraud label are required; the four balance fields are intentionally nullable and retain source nulls. It excludes source `initiator` and `recipient` values completely and never fabricates a calendar date or transaction identifier.

The console never downloads or rebuilds data on request. It opens the approved snapshot read-only when present; otherwise it explicitly stays in demo-fixture mode. After the verified sources are fetched, `uv run guardrails data profile --source <csv> --source <csv>` emits a row-free schema/quality profile before curation. The manually dispatched `Approved data release` workflow profiles both named files and can publish snapshot/profile/provenance/benchmark artifacts only after its gates pass.

See `docs/evaluation.md`, `docs/architecture.md`, `docs/deployment.md`, and `portfolio/project.json`. Azure is a non-applied future blueprint only.

# Text-to-SQL Interface with Guardrails and Hallucination Detection

## Status

Private, local-first prototype. It demonstrates guardrails around a deliberately small, deterministic text-to-SQL catalog; it is not deployed, not a bank system, and not production-ready.

## One analyst workflow

```bash
uv sync --group dev
uv run guardrails "What is the total amount of completed payments?"
uv run guardrails "Delete all payments"
```

The first command returns a `trusted` verdict with generated SQL, validation checks, a result preview, a trace ID, latency, and local cost `$0`. The second returns `refused`: only exact questions from the versioned catalog are supported. Start the API with `uv run uvicorn guardrails.api:app --reload`; then POST `{"question":"Show completed payments by country."}` to `/v1/query`.

Docker path: `docker compose up --build`.

## Guardrails

Every candidate query is parsed before execution. The validator permits exactly one `SELECT`, allows only `fact_payments` and `dim_customer` and their documented columns, blocks unsafe functions, performs schema verification with `EXPLAIN`, and adds `LIMIT 100`. Unsupported requests, malformed SQL, unknown tables/columns, and write operations are refused before DuckDB execution.

## Data, evidence, and limitations

The fixture at `data/fixtures/payments.json` is a small hand-authored normalized synthetic demo fixture; it does not contain rows downloaded from the source dataset, real customer data, cardholder data, or bank data. Its schema/domain inspiration is disclosed in `data/PROVENANCE.md`. The source is MoMTSim V2, published 2024-10-29 under CC BY 4.0. Evaluation runs are local and reproducible: `uv run python scripts/run_evaluation.py` regenerates `evaluation/report.json` and `evaluation/report.md`.

See `docs/evaluation.md`, `docs/architecture.md`, `docs/deployment.md`, and `portfolio/project.json`. Azure is a non-applied future blueprint only.

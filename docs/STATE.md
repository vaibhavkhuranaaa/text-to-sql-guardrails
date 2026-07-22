# Build state

## Current goal

Deliver a live, interactive governed Text-to-SQL experience with an educational UI, an approved data table view, classified example queries, an explicit limitations/improvements handoff, and enforceable SQL quality/resource controls.

## Completed

- Implemented local FastAPI/CLI, deterministic catalog, SQL validation, read-only DuckDB execution, fixture provenance, evaluation, Docker path, architecture asset, future-only Bicep, and CI checks.
- Verified locally on 2026-07-22: `uv run ruff format .`, `uv run pytest -q` (8 passed), `uv run ruff check .`, evaluation regeneration, manifest validation, Docker Compose configuration, and `git diff --check`.
- Evidence: `evaluation/report.json`, `evaluation/report.md`, `portfolio/assets/system.png`, and `data/PROVENANCE.md`.
- Graphify code context refreshed after implementation: 49 nodes, 84 edges, 12 communities. The ignored graph is AST-only because no semantic-extraction credential is configured.
- Added v2 Azure Foundry proposal contract, an explicit short-lived approval step, snapshot revalidation, a curated identifier-excluding semantic catalog, and an expanded bounded read-only SQL policy.
- Added source-release scaffolding: owner checksum gate, ignored raw/snapshot storage, normalization quality checks, environment-gated release workflow, and local benchmark script.
- Added row-free profiling for both reviewed CSVs, a proposal-review console (scenario cards, proposed read-only SQL, lineage, policy/explain review, explicit approval, preview, and export-disabled boundary), and advanced-policy evaluation cases.
- Recorded owner-verified V2 source checksums and generated row-free profiles for both files. The profile confirms a shared ten-column source schema; `initiator` and `recipient` are excluded as account identifiers.
- Built a local approved snapshot from `MoMTSim_20240722202413_1000_dataset.csv`: 4,225,958 transactions, source SHA-256 `99fd07c3a9d3c4bd6d3462240058ca19d0d9e9284683f78bf77542ff7fcc05e7`, and no source identifiers retained. The ignored snapshot metadata and benchmark are generated local evidence.
- Replaced API-key authentication with Microsoft Entra ID via `DefaultAzureCredential`. Local development uses Azure CLI login; deployed workloads use managed identity. API keys are not accepted by the adapter.
- Verified the existing owner-controlled Azure OpenAI deployment with Entra ID: a live `gpt-5-mini` proposal was generated and passed policy validation against the approved snapshot. The adapter now uses `/openai/v1/chat/completions`, sends the deployment name as `model`, and omits unsupported `temperature: 0` for GPT-5.
- Live read-only execution has not been completed: repeated test-process proposals varied only in safe SQL form, and each short-lived in-memory proposal expired with that process before a persistent approval could be applied. No source rows, identifiers, writes, or external data access occurred.
- Replaced process-local proposal state with a SQLite-backed, five-minute, single-use approval store. It persists across requests and can be pointed at an owner-mounted private volume with `GUARDRAILS_PROPOSAL_STORE`; it never stores analyst questions or result rows.
- Added enforceable local query controls: 512MB DuckDB memory cap, two query threads, no temporary-disk spill, a 100-row preview, and an interrupting three-second execution budget. The runtime was checked directly and reported 488.2 MiB effective memory, two threads, and zero temporary-disk bytes.
- Added clean console endpoints and UI content for a curated data table, lineage disclosure, and Beginner/Intermediate/Advanced prompt examples. API tests verify that previews exclude `initiator` and `recipient`.
- Verified a real Microsoft Entra-authenticated Foundry v2 lifecycle in one persistent local server process: a `gpt-5-mini` proposal for transaction counts by transaction type was policy-allowed, explicitly approved once, revalidated, and executed read-only against `fact_transactions`, returning five aggregate rows. This is local integration evidence only; it is not a public URL, deployment, or latency/SLO claim.
- Corrected the approved snapshot contract to preserve nullable balance fields while requiring simulation step, transaction type, amount, and fraud label. Rebuilt the ignored local snapshot from the re-verified MoMTSim SHA-256 source and expanded evaluation coverage for explicit NULL bucketing plus ranking-with-order acceptance/ranking-without-order refusal.
- Verified locally on 2026-07-22: re-verified source SHA-256, rebuilt the local 4,225,958-row approved snapshot, regenerated benchmark/evaluation evidence (18 local fixture cases), `uv run ruff format .`, `uv run ruff check .`, `uv run pytest -q` (25 passed; one upstream Starlette deprecation warning), manifest validation, Docker Compose configuration, and `git diff --check`.

## Active branch / PR

- `feat/text-to-sql-guardrails-initial-delivery` / not opened

## Next bounded task

Mount the provisioned Azure Files store, configure single-tenant Microsoft Entra authentication, and verify unauthenticated denial before enabling public ingress. Do not claim a public live link until that authenticated deployment succeeds.

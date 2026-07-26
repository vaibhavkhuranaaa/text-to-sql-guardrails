# Text-to-SQL Interface with Guardrails and Hallucination Detection

[![CI](https://github.com/vaibhavkhuranaaa/text-to-sql-guardrails/actions/workflows/ci.yml/badge.svg)](https://github.com/vaibhavkhuranaaa/text-to-sql-guardrails/actions/workflows/ci.yml) ![Publication](https://img.shields.io/badge/publication-review_required-5b6470) ![Production claim](https://img.shields.io/badge/production_claim-no-18794e)

> An approval-gated analyst console that turns bounded natural-language questions into policy-checked, read-only SQL over disclosed synthetic data.

## Executive overview

| Question | Reviewed fact |
| --- | --- |
| Problem | How can analysts use natural-language SQL proposals without letting model output execute unchecked? |
| Intended user | A data analyst or technical reviewer evaluating governed natural-language access to a classified synthetic payments model. |
| Decision supported | Whether a proposed analytical query is within the classified schema and safe enough for one reviewed execution. |
| Outcome | Reviewers can inspect SQL, assumptions, schema lineage, policy checks, and a bounded result preview before one single-use execution; unsafe, malformed, identifier-exposing, and hallucinated-schema queries fail closed. |
| Try it | [Open the reviewed demo](https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io) |
| Important boundary | Anonymous, non-production demonstration using synthetic data only. It is not a bank system, fraud decision service, security posture, availability claim, or production-readiness claim. |

## What the system does

- Curated semantic catalog and explicit data classification
- Azure OpenAI SQL proposal generation through Microsoft Entra ID
- Parser-backed table, column, function, statement, and resource policy checks
- Human review with short-lived single-use approval
- Policy and snapshot revalidation before read-only DuckDB execution
- Bounded result preview with privacy-preserving lifecycle events

## Visual architecture

![System architecture showing an analyst, synthetic data and semantic catalog, FastAPI proposal and approval interfaces, Azure OpenAI, SQLGlot and DuckDB validation, ephemeral approval storage, read-only execution, privacy boundary, telemetry, deployment controls, and evaluation.](portfolio/assets/system.svg)

Canonical editable source: [`architecture/system.mmd`](architecture/system.mmd). The SVG and PNG are deterministic generated assets; `system.freshness.json` records their source hash and renderer.

## End-to-end workflow

- Choose or enter an analytical question over the disclosed semantic catalog
- Inspect proposed SQL, assumptions, referenced fields, policy checks, and EXPLAIN summary
- Approve one short-lived token-bound execution or let the system refuse the request
- Review a maximum 100-row preview that excludes identifier-like fields

## Technology stack

| Technology | Role | Asset provenance |
| --- | --- | --- |
| <img src="portfolio/assets/technology/python.svg" width="20" height="20" alt="" /> Python | Service, policy, data, and evaluation language | Simple Icons 16.27.0 (CC0-1.0) |
| <img src="portfolio/assets/technology/fastapi.svg" width="20" height="20" alt="" /> FastAPI | Proposal, approval, status, and execution interfaces | Simple Icons 16.27.0 (CC0-1.0) |
| <img src="portfolio/assets/technology/duckdb.svg" width="20" height="20" alt="" /> DuckDB | Read-only analytical execution engine | Simple Icons 16.27.0 (CC0-1.0) |
| SQLGlot | Parser-backed SQL policy | Visible text fallback; no approved local logo registered |
| Azure OpenAI | Natural-language SQL proposal generation | Visible text fallback; no approved local logo registered |
| Microsoft Entra ID | Credential-free Azure authentication | Visible text fallback; no approved local logo registered |
| Azure Container Apps | Temporary scale-to-zero hosting | Visible text fallback; no approved local logo registered |
| <img src="portfolio/assets/technology/docker.svg" width="20" height="20" alt="" /> Docker | Reproducible application boundary | Simple Icons 16.27.0 (CC0-1.0) |
| <img src="portfolio/assets/technology/opentelemetry.svg" width="20" height="20" alt="" /> OpenTelemetry | Privacy-preserving lifecycle telemetry | Simple Icons 16.27.0 (CC0-1.0) |

## Quick start

### Install and verify

```bash
uv sync --locked --group dev
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
```

### Run the deterministic walkthrough

```bash
uv run guardrails "What is the total amount of completed payments?"
uv run guardrails "Delete all payments"
```

### Run the local analyst console

```bash
uv run uvicorn guardrails.api:app --reload
```

## Demonstration workflow

**Generate, review, and approve one bounded query**

- Choose or enter an analytical question over the disclosed semantic catalog
- Inspect proposed SQL, assumptions, referenced fields, policy checks, and EXPLAIN summary
- Approve one short-lived token-bound execution or let the system refuse the request
- Review a maximum 100-row preview that excludes identifier-like fields

## Evaluation

| Measure | Dataset / scope | Method | Evidence | Limitation |
| --- | --- | --- | --- | --- |
| deterministic policy outcomes: 18/18 | 18 trusted and refused cases over the committed synthetic fixture | uv run python scripts/run_evaluation.py against the committed synthetic fixture | [evaluation.local-policy](evaluation/report.json) | The fixture and case set are intentionally bounded and do not establish open-ended semantic correctness. |
| public status-only checks: 6/6 | Root, evaluation, examples, safe preview, active fixture boundary, and deployed control configuration | HTTP checks with response bodies limited to status and disclosed fixture metadata | [deployment.anonymous-live-demo](evidence/deployment/anonymous-live-demo.json), [security.demo-fixture-boundary](evidence/deployment/anonymous-live-demo.json) | Status-only checks do not establish availability, caller authorization, durable limits, or production readiness. |

Evaluation mode: **deterministic local policy evaluation plus live status-only integration checks on an anonymous demo**. These results are project evidence, not a production SLO.

## Data disclosure

| Classification | Source | Permitted use | Excluded data |
| --- | --- | --- | --- |
| synthetic | Hand-authored synthetic demo fixture inspired by the MoMTSim V2 synthetic mobile-money dataset (DOI 10.17632/zhj366m53p.2) | Portfolio demonstration, deterministic evaluation, and bounded analyst-workflow review | Source initiator and recipient account identifiers; Real customer, cardholder, bank, credential, and personal data; Identifier-like fields in model context and public result previews; The locally generated 4,225,958-row approved DuckDB snapshot |

License / provenance: MoMTSim V2 is CC BY 4.0; the deployed rows are repository-authored synthetic fixtures rather than redistributed source rows

## Security and privacy boundaries

| Control | Implementation | Evidence | Known limitation |
| --- | --- | --- | --- |
| Parser-backed read-only SQL policy | SQLGlot validates statement shape, functions, tables, columns, identifier projection, and resource boundaries before DuckDB EXPLAIN or execution. | [evaluation.local-policy](evaluation/report.json) | A syntactically safe query can still be semantically wrong, so human review remains mandatory. |
| Data and container boundary | Raw source data and approved snapshots are excluded from the image; model context and previews omit identifier-like fields. | [security.container-data-boundary](.dockerignore and scripts/verify_container_boundary.py), [disclosure.synthetic-data](data/PROVENANCE.md and data/source_manifest.json) | The public fixture remains a small hand-authored synthetic demonstration. |
| Short-lived single-use approval | Execution requires a five-minute token-bound approval and revalidates SQL policy plus the active snapshot checksum. | [integration.entra-proposal-lifecycle](docs/HANDOFF.md) | Approval state is ephemeral SQLite and is not durable across restarts or replicas. |
| Anonymous-demo controls | The public revision exposes rate, proposal-budget, and aggregate status controls. | [deployment.anonymous-live-demo](evidence/deployment/anonymous-live-demo.json), [security.demo-fixture-boundary](evidence/deployment/anonymous-live-demo.json) | Controls are process-local and reset after scale-to-zero or restart; there is no caller authorization. |
| Bounded operational observation | The existing non-production target has a redacted owner notification route, a $30 monthly budget, and aggregate stderr and latency alerts. | [operational.m6-alert-readiness](evidence/m6/operational-observation.json) | This creates no availability SLO, on-call rota, durable-state guarantee, or production claim. |

## Deployment state

| Provider | Runtime | State | Exposure | Verified | Production claim |
| --- | --- | --- | --- | --- | --- |
| Azure Container Apps | Scale-to-zero FastAPI container using the committed demo fixture and ephemeral SQLite proposal state | live | anonymous | 2026-07-24T04:25:22.107862Z | No |

## Technology decisions and trade-offs

| Decision | Why | Alternative | Trade-off |
| --- | --- | --- | --- |
| Azure OpenAI with Microsoft Entra ID | Keeps provider credentials out of the repository and supports managed identity in Azure. | Static API keys | Identity and role configuration add operational setup but remove long-lived application secrets. |
| SQLGlot plus DuckDB EXPLAIN | Provides parser-backed structural policy and database-level validation before execution. | Regex filtering or direct model execution | The policy intentionally rejects ambiguous or unsupported SQL and still requires semantic human review. |
| Ephemeral SQLite approval store | Provides five-minute single-use approval persistence for a one-replica anonymous demo. | Managed transactional database | Simple and low-cost, but restart-sensitive and unsuitable for protected multi-replica hosting. |

## Cost boundaries

| Component | Boundary | Implication |
| --- | --- | --- |
| Azure Container Apps | Consumption profile with zero-to-one replicas and no automatic expiry. | The demo can cold start; no availability SLO is claimed. |
| Azure OpenAI | Proposal-only model call with a per-process budget and a classified semantic catalog. | Local latency and cost observations are not production cost or performance claims. |
| Proposal and analytics storage | Ephemeral SQLite plus a read-only synthetic fixture in the public demo. | Durable multi-replica operation requires an owner-approved transactional store. |

## Known limitations

- The current endpoint is anonymous and has no caller authorization.
- The deployed rate and proposal-budget controls are process-local and reset after scale-to-zero or restart.
- Approval state is ephemeral and single-replica.
- The model can still propose semantically wrong SQL, so human review remains mandatory.
- The anonymous demo has no automatic expiry; the owner remains responsible for ongoing cost and operational review.

## Scalability roadmap

- Replace ephemeral SQLite with an owner-approved transactional store and prove cross-replica single-use consumption
- Enable single-tenant Microsoft Entra authentication and verify unauthenticated denial
- Replace process-local rate and proposal budgets with durable distributed controls before multi-replica hosting
- Add alerting, budget ownership, availability/error monitoring, and an owner-approved load envelope
- Expand semantic evaluation with reviewer-approved equivalent SQL rather than literal query matching

## Repository structure

| Path | Purpose |
| --- | --- |
| `src/guardrails/` | API, proposal, approval, SQL policy, execution, data, and telemetry code. |
| `evaluation/` | Deterministic policy cases and generated aggregate report. |
| `data/` | Synthetic fixture, provenance, classification, and ignored local release artifacts. |
| `evidence/deployment/` | Status-only deployment verification records. |
| `architecture/system.mmd` | Canonical editable architecture source. |
| `portfolio/` | Public evidence manifest and generated presentation assets. |

## Reproduction and verification

| Check | Command | Evidence |
| --- | --- | --- |
| Format and lint | `uv run ruff format --check . && uv run ruff check .` | Command output |
| Tests | `uv run pytest -q` | Command output |
| Evaluation and manifest | `uv run python scripts/run_evaluation.py && uv run python scripts/validate_manifest.py` | [evaluation.local-policy](evaluation/report.json) |
| Container configuration | `docker compose config >/dev/null` | Command output |

## Evidence index

| ID | Kind | Claim | Method | Result |
| --- | --- | --- | --- | --- |
| [`evaluation.local-policy`](evaluation/report.json) | evaluation | All 18 deterministic policy cases matched their expected trusted or refused outcomes. | uv run python scripts/run_evaluation.py against the committed synthetic fixture | 18/18 expected outcomes |
| [`deployment.anonymous-live-demo`](evidence/deployment/anonymous-live-demo.json) | deployment | Six status-only public route, fixture-boundary, and deployed-control checks passed for the anonymous live demo. | HTTP checks with response bodies limited to status and disclosed fixture metadata | revision 0000007 / 6 checks passed |
| [`security.demo-fixture-boundary`](evidence/deployment/anonymous-live-demo.json) | security | The active public revision reports the committed demo fixture, not the local approved snapshot. | Verified /v1/status snapshot state and fixture SHA-256 | demo_fixture |
| [`security.container-data-boundary`](.dockerignore and scripts/verify_container_boundary.py) | security | The container build context excludes raw source files and data/approved artifacts while retaining only the disclosed fixture and aggregate evidence. | Build the image and run the boundary verifier inside that image | verified in Azure-built image sha256:fb11bdf14321e18fb835670154b737a3d4ff6d81c5c29ebba4f79c9c47bc7e53 |
| [`disclosure.synthetic-data`](data/PROVENANCE.md and data/source_manifest.json) | disclosure | The deployed dataset is hand-authored synthetic data and source account identifiers are excluded from the approved snapshot contract. | Versioned provenance, license, source checksums, and curated-field classification | synthetic / CC BY 4.0 source attribution |
| [`integration.entra-proposal-lifecycle`](docs/HANDOFF.md) | review | An owner-authenticated local lifecycle generated, approved once, revalidated, and executed a bounded aggregate proposal. | Status-level local integration verification using Microsoft Entra ID; no token, question, SQL, or rows retained | verified locally; not a public SLO |
| [`operational.m6-alert-readiness`](evidence/m6/operational-observation.json) | operational | The anonymous non-production target has a redacted owner notification route, bounded budget thresholds, and aggregate stderr and latency alerts. | Read-only Azure configuration observation with recipient and log data excluded | one enabled action group, $30 monthly budget, and two enabled five-minute scheduled-query alerts |

## License and attribution

Source code uses the repository license. MoMTSim V2 inspiration is attributed under CC BY 4.0; deployed rows are repository-authored synthetic fixtures.

Technology marks are local copies generated from the pinned Simple Icons package where a canonical mark is available; every mark has a visible text label. Mermaid-generated architecture assets are derived from the canonical source in this repository.

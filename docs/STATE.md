# State

## Independent axes

- Lifecycle: `first-demo`
- Deployment: `temporary-demo`
- Exposure: `anonymous`
- Production claim: `false`
- Publication: exact-SHA portfolio approval pending final catalog synchronization
- Contract health: first-demo and temporary-demo publication targets pass; protected-hosting gates remain open

## Current evidence

- Public endpoint: `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io`
- Revision: `ca-text-sql-guardrails-dev--0000007`
- Image: `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:6ba0f20`
- Digest: `sha256:fb11bdf14321e18fb835670154b737a3d4ff6d81c5c29ebba4f79c9c47bc7e53`
- Status-only verification: `evidence/deployment/temporary-demo.json`, observed `2026-07-24T04:25:22.107862Z`
- Scale: Consumption profile, zero-to-one replicas
- Owner-controlled expiry: `2026-08-06T23:59:59Z`
- Local policy evaluation: `evaluation/report.json`, 18 of 18 expected outcomes
- Architecture asset: `portfolio/assets/system.png`; source: `architecture/system.mmd`
- Data contract: `data/PROVENANCE.md` and `data/source_manifest.json`

## Implemented

- FastAPI/CLI, deterministic v1 walkthrough, Azure OpenAI v2 proposals through Microsoft Entra ID, explicit single-use approval, SQLGlot policy, DuckDB EXPLAIN, read-only execution, resource limits, safe previews, and privacy-preserving lifecycle logs.
- Checksum-pinned synthetic-data profiling/build pipeline that excludes source `initiator` and `recipient` identifiers from approved snapshots.
- Structured manifest v2 with deployment, disclosure, evidence, stakeholder narrative, limitations, scalability roadmap, and evidence-linked résumé candidates.
- Source-level anonymous-demo controls: per-client minute limit using a hashed key, per-process proposal budget, expiry refusal, aggregate status counters, and status-only monitoring events.
- Container boundary: `.dockerignore` excludes raw and approved data; CI builds the image and runs `scripts/verify_container_boundary.py` inside it.
- Exact-SHA portfolio preview dispatch and owner-gated temporary-demo verification workflow.

## Current deployment limitations

- Rate, proposal-budget, and counter controls are process-local and reset after scale-to-zero or restart.
- No caller identity or authorization.
- Proposal state is SQLite under `/tmp`, single-replica, and restart-sensitive.
- No production monitoring, alerting, availability evidence, load envelope, or SLO.
- The locally generated 4,225,958-row approved snapshot is ignored and must never enter the image; the live status reports only the committed demo fixture.

## Repository state

- Branch: `feat/text-to-sql-guardrails-initial-delivery`
- Remote: public `vaibhavkhuranaaa/text-to-sql-guardrails`
- Draft PR: `https://github.com/vaibhavkhuranaaa/text-to-sql-guardrails/pull/1`
- Workspace cleanup: `data/.DS_Store` was moved to macOS Trash as `text-to-sql-guardrails-data.DS_Store` under the task's explicit deletion authority. It can be restored from Trash.
- Graphify: fresh 227-node, 396-edge graph across code and authoritative documentation; source fingerprint stamped at `2026-07-23T20:49:16.984Z`

## Next gate

Local verification is complete: Ruff format/check passed, 29 tests passed with one Starlette deprecation warning, the evaluation and both first-demo manifest validators passed, Docker Compose resolved, `git diff --check` passed, and Graphify is fresh. A local in-image boundary run remains unavailable because this machine has no Docker application/daemon; CI contains the required build-and-inspect proof.

The public remote, exact commit, Azure-built image boundary, replacement revision, live controls, and public routes are verified. Final publication requires pinning this evidence commit in the portfolio registry and synchronizing all consumers. Authentication and durable storage remain explicit limitations rather than claims. The workspace owner remains responsible for reviewing or tearing down the anonymous demo by `2026-08-06T23:59:59Z`.

## Workspace stabilization — 2026-07-23

- Stable cleanup record commit: `3b49ce43642afd09a72f8ab779fba71d8eb1ffc0`
- Verification: the only authorized Trash target is absent from the worktree and recoverable from macOS Trash; repository checks remain as recorded above.
- Rollback baseline: `9f93ae36def6a9ce627a322f8ac7410ed1c6da20`
- Next action: owner reviews or tears down the anonymous temporary demo by its recorded expiry.

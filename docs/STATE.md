# State

Exact-SHA deployment automation is declared in `portfolio/release.json`. The workflow builds an immutable ACR image, checks its container boundary, updates only the existing Container App, verifies the deployed SHA and anonymous-demo controls, and uploads a receipt.

## Independent axes

- Lifecycle: `first-demo`
- Deployment: `live`
- Exposure: `anonymous`
- Production claim: `false`
- Publication: approved at exact source commit `9b05287ce2598ad82920fc1c1dd19c1b62aec3f9`
- Contract health: first-demo and live publication targets pass; protected-hosting gates remain open

## Current evidence

- Public endpoint: `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io`
- Revision: `ca-text-sql-guardrails-dev--0000007`
- Image: `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:6ba0f20`
- Digest: `sha256:fb11bdf14321e18fb835670154b737a3d4ff6d81c5c29ebba4f79c9c47bc7e53`
- Status-only verification: `evidence/deployment/anonymous-live-demo.json`, observed `2026-07-24T04:25:22.107862Z`
- Scale: Consumption profile, zero-to-one replicas
- Local policy evaluation: `evaluation/report.json`, 18 of 18 expected outcomes
- Architecture asset: `portfolio/assets/system.png`; source: `architecture/system.mmd`
- Data contract: `data/PROVENANCE.md` and `data/source_manifest.json`

## Implemented

- FastAPI/CLI, deterministic v1 walkthrough, Azure OpenAI v2 proposals through Microsoft Entra ID, explicit single-use approval, SQLGlot policy, DuckDB EXPLAIN, read-only execution, resource limits, safe previews, and privacy-preserving lifecycle logs.
- Checksum-pinned synthetic-data profiling/build pipeline that excludes source `initiator` and `recipient` identifiers from approved snapshots.
- Structured manifest v2 with deployment, disclosure, evidence, stakeholder narrative, limitations, scalability roadmap, and evidence-linked résumé candidates.
- Source-level anonymous-demo controls: per-client minute limit using a hashed key, per-process proposal budget, aggregate status counters, and status-only monitoring events.
- Container boundary: `.dockerignore` excludes raw and approved data; CI builds the image and runs `scripts/verify_container_boundary.py` inside it.
- Exact-SHA release verification workflow; external consumers independently synchronize from the published manifest.

## Current deployment limitations

- Rate, proposal-budget, and counter controls are process-local and reset after scale-to-zero or restart.
- No caller identity or authorization.
- Proposal state is SQLite under `/tmp`, single-replica, and restart-sensitive.
- No production monitoring, alerting, availability evidence, load envelope, or SLO.
- The locally generated 4,225,958-row approved snapshot is ignored and must never enter the image; the live status reports only the committed demo fixture.

## Repository state

- Branch: `main`
- Remote: public `vaibhavkhuranaaa/text-to-sql-guardrails`
- Head: `ab2e2b590dc657cfa85cb86dc7078ff986f67d40` before this no-expiry change
- Workspace cleanup: `data/.DS_Store` was moved to macOS Trash as `text-to-sql-guardrails-data.DS_Store` under the task's explicit deletion authority. It can be restored from Trash.
- Graphify: fresh 227-node, 396-edge graph across code and authoritative documentation; source fingerprint stamped at `2026-07-23T20:49:16.984Z`

## Next gate

Local verification is complete: Ruff format/check passed, 29 tests passed with one Starlette deprecation warning, the evaluation and both first-demo manifest validators passed, Docker Compose resolved, `git diff --check` passed, and Graphify is fresh. A local in-image boundary run remains unavailable because this machine has no Docker application/daemon; CI contains the required build-and-inspect proof.

The public remote, Azure-built image boundary, replacement revision, live controls, and public routes are verified. Authentication and durable storage remain explicit limitations rather than claims. The anonymous demo has no automatic expiry; the workspace owner remains responsible for ongoing cost and operational review.

## No-expiry transition — pending exact-SHA deployment

- The source contract now classifies the deployment as anonymous, non-production `live` and removes all expiry configuration, runtime controls, workflow inputs, and evidence fields.
- Local checks passed: Ruff format/check, 29 tests, deterministic evaluation, live-profile manifest validation, Docker Compose configuration, presentation validation, and `git diff --check`.
- The local Docker daemon is unavailable, so the in-image data-boundary proof remains a CI release-workflow check.
- The committed main revision must be deployed before `evidence/deployment/anonymous-live-demo.json` can be refreshed with a new exact source SHA, image digest, and status-only observation.
- Graphify was used to scope this transition; regenerate it after the authoritative no-expiry revision is committed so its fingerprint matches the new source state.

## Workspace stabilization — 2026-07-23

- Stable cleanup record commit: `3b49ce43642afd09a72f8ab779fba71d8eb1ffc0`
- Verification: the only authorized Trash target is absent from the worktree and recoverable from macOS Trash; repository checks remain as recorded above.
- Rollback baseline: `9f93ae36def6a9ce627a322f8ac7410ed1c6da20`
- Next action: merge the no-expiry revision so the declared release workflow can verify and record its exact deployed SHA.

- Checkpoint: 2026-07-24T05:30:15.531Z — Presentation handoff completed for text-to-sql-guardrails.

- `sh -lc uv run ruff format --check . && uv run ruff check .` passed in 146 ms.
- `sh -lc uv run pytest -q` passed in 877 ms.
- `sh -lc uv run python scripts/run_evaluation.py && uv run python scripts/validate_manifest.py` passed in 358 ms.
- `sh -lc docker compose config >/dev/null` passed in 125 ms.
- `node scripts/project-presentation.mjs validate --check` passed in 36 ms.
- `sh -lc ! rg -n '(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----)' --glob '!uv.lock' --glob '!package-lock.json' .` passed in 96 ms.
- `git diff --check` passed in 10 ms.

Public membership and exact-SHA approval were not changed.

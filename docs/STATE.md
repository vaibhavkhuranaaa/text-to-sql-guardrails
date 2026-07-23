# State

## Independent axes

- Lifecycle: `first-demo`
- Deployment: `temporary-demo`
- Exposure: `anonymous`
- Production claim: `false`
- Publication: `absent`
- Contract health: first-demo target `pass`; publication `fail` because no remote/source URL and protected-hosting gates remain open

## Current evidence

- Public endpoint: `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io`
- Revision: `ca-text-sql-guardrails-dev--0000006`
- Image: `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:20260723-3`
- Digest: `sha256:9ea98f96e2f23f84d50c148c3699c65205db66a4076e412b0ead001d94923cc7`
- Status-only verification: `evidence/deployment/temporary-demo.json`, observed `2026-07-23T20:43:49.489473Z`
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

- Revision `0000006` predates the new rate, process-budget, expiry, and counter code.
- No caller identity or authorization.
- Proposal state is SQLite under `/tmp`, single-replica, and restart-sensitive.
- No production monitoring, alerting, availability evidence, load envelope, or SLO.
- The locally generated 4,225,958-row approved snapshot is ignored and must never enter the image; the live status reports only the committed demo fixture.

## Repository state

- Branch: `feat/text-to-sql-guardrails-initial-delivery`
- Remote: private `vaibhavkhuranaaa/text-to-sql-guardrails`
- Draft PR: `https://github.com/vaibhavkhuranaaa/text-to-sql-guardrails/pull/1`
- Pre-existing unrelated item to preserve: untracked `data/.DS_Store`
- Graphify: fresh 227-node, 396-edge graph across code and authoritative documentation; source fingerprint stamped at `2026-07-23T20:49:16.984Z`

## Next gate

Local verification is complete: Ruff format/check passed, 29 tests passed with one Starlette deprecation warning, the evaluation and both first-demo manifest validators passed, Docker Compose resolved, `git diff --check` passed, and Graphify is fresh. A local in-image boundary run remains unavailable because this machine has no Docker application/daemon; CI contains the required build-and-inspect proof.

The private remote and draft PR now exist. Publication remains blocked until the PR is reviewed, a replacement deployment proves limits/expiry, authentication and durable storage decisions are resolved, an exact-SHA preview passes, and the portfolio registry receives owner approval.

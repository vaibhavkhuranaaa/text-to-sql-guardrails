# Handoff

## Resume point

Read `AGENTS.md`, `docs/STATE.md`, `portfolio/project.json`, and the structured deployment evidence. Query the fresh Graphify graph first for covered code paths and fall back to direct inspection where needed.

The project is a verified anonymous temporary demo, not an undeployed local prototype and not a production service. The manifest now reflects that distinction. The current public revision is still `0000006`; no deployment was performed during the orchestration migration.

## Work completed in the current migration

- Reconciled README, state, handoff, architecture, product, deployment, and manifest facts.
- Added a v2 first-demo evidence contract with exact deployment revision/digest, synthetic-data disclosure, limitations, roadmap, and evidence-linked résumé bullets.
- Verified five status-only public checks without retaining tokens, questions, SQL, or result rows.
- Added rate, process-budget, expiry, and aggregate status controls in source.
- Excluded `data/Raw`, `data/raw`, and `data/approved` from the container context and added an in-image boundary verifier.
- Replaced placeholder portfolio dispatch/release workflows with exact-SHA preview and owner-gated verification workflows.

## Preserve

- `data/.DS_Store` was moved to macOS Trash as `text-to-sql-guardrails-data.DS_Store` under explicit owner authority; restore it from Trash only if needed.
- Raw CSVs, approved snapshots, profiles, metadata, benchmarks, and proposal stores are local/ignored artifacts.
- Do not expose the owner-controlled Azure endpoint/deployment environment configuration as committed runtime values.
- Do not describe the temporary URL as authenticated, rate-limited, monitored, durable, production-ready, or live-verified after these source changes; revision `0000006` predates them.

## Verification result

- Ruff format/check passed.
- Pytest passed 29 tests with one Starlette deprecation warning.
- Evaluation regenerated and both first-demo manifest validators passed.
- Docker Compose resolved and `git diff --check` passed.
- Graphify was regenerated and source-fingerprint stamped.
- The authorized `.DS_Store` cleanup is recoverable from macOS Trash.
- The in-image boundary proof could not run locally because no Docker application/daemon exists; CI now performs it after image construction.
- The private remote is `vaibhavkhuranaaa/text-to-sql-guardrails` and draft PR 1 contains the first-demo migration. Keep it draft until checks and owner review complete.

## Later protected-hosting gate

Use single-tenant Microsoft Entra authentication, an owner-approved transactional proposal store, verified cross-replica single-use behavior, deployed rate/budget/expiry controls, monitoring and alerting, and an owner-approved cost/load envelope. Deployment, public visibility, publication, and teardown remain separate owner actions.

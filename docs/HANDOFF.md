# Handoff

## Resume point

Read `AGENTS.md`, `docs/STATE.md`, `portfolio/project.json`, and the structured deployment evidence. Query the fresh Graphify graph first for covered code paths and fall back to direct inspection where needed.

The project is a verified anonymous temporary demo, not an undeployed local prototype and not a production service. Replacement revision `0000007` deploys the source-level rate, process-budget, expiry, and status controls and scales from zero to one replica.

The authorized local cleanup is recorded at `3b49ce43642afd09a72f8ab779fba71d8eb1ffc0`. Roll it back only by restoring the named file from macOS Trash or through a reviewed revert; do not reset to `9f93ae36def6a9ce627a322f8ac7410ed1c6da20`.

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
- Do not describe the temporary URL as authenticated, durably rate-limited, monitored, or production-ready. The deployed limits are process-local and reset after scale-to-zero or restart.

## Verification result

- Ruff format/check passed.
- Pytest passed 29 tests with one Starlette deprecation warning.
- Evaluation regenerated and both first-demo manifest validators passed.
- Docker Compose resolved and `git diff --check` passed.
- Graphify was regenerated and source-fingerprint stamped.
- The authorized `.DS_Store` cleanup is recoverable from macOS Trash.
- The in-image boundary proof could not run locally because no Docker application/daemon exists; CI now performs it after image construction.
- The public remote is `vaibhavkhuranaaa/text-to-sql-guardrails`; the exact source commit and replacement deployment are anonymously verifiable. Draft PR 1 remains an unmerged review record.

## Later protected-hosting gate

Use single-tenant Microsoft Entra authentication, an owner-approved transactional proposal store, verified cross-replica single-use behavior, monitoring and alerting, and an owner-approved cost/load envelope before protected hosting. Publication does not convert this temporary anonymous demo into a production service.

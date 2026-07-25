# Handoff

## Minimal resume

Read `AGENTS.md`, `docs/STATE.md`, this file, and only the paths named by the task. Public release uses `portfolio/release.json` and `.github/workflows/deploy.yml`; it requires an approved exact SHA and explicit approval for the existing paid Azure target.

## Resume point

Read `AGENTS.md`, `docs/STATE.md`, `portfolio/project.json`, and the structured deployment evidence. Query the fresh Graphify graph first for covered code paths and fall back to direct inspection where needed.

The project is an anonymous live demo, not an undeployed local prototype and not a production service. It deploys source-level rate, process-budget, and status controls and scales from zero to one replica.

Portfolio publication is approved at exact evidence commit `9b05287ce2598ad82920fc1c1dd19c1b62aec3f9`. The portfolio site, Resume Creator, and public GitHub index were regenerated from the same three-project approved catalog.

The authorized local cleanup is recorded at `3b49ce43642afd09a72f8ab779fba71d8eb1ffc0`. Roll it back only by restoring the named file from macOS Trash or through a reviewed revert; do not reset to `9f93ae36def6a9ce627a322f8ac7410ed1c6da20`.

## Work completed in the current migration

- Reconciled README, state, handoff, architecture, product, deployment, and manifest facts.
- Added a v2 first-demo evidence contract with exact deployment revision/digest, synthetic-data disclosure, limitations, roadmap, and evidence-linked résumé bullets.
- Verified five status-only public checks without retaining tokens, questions, SQL, or result rows.
- Added rate, process-budget, and aggregate status controls in source.
- Excluded `data/Raw`, `data/raw`, and `data/approved` from the container context and added an in-image boundary verifier.
- Uses exact-SHA deployment and release-verification workflows; external portfolio consumers synchronize independently.

## Preserve

- `data/.DS_Store` was moved to macOS Trash as `text-to-sql-guardrails-data.DS_Store` under explicit owner authority; restore it from Trash only if needed.
- Raw CSVs, approved snapshots, profiles, metadata, benchmarks, and proposal stores are local/ignored artifacts.
- Do not expose the owner-controlled Azure endpoint/deployment environment configuration as committed runtime values.
- Do not describe the anonymous URL as authenticated, durably rate-limited, monitored, or production-ready. The deployed limits are process-local and reset after scale-to-zero or restart.

## Verification result

- Ruff format/check passed.
- Pytest passed 29 tests with one Starlette deprecation warning.
- Evaluation regenerated and both first-demo manifest validators passed.
- Docker Compose resolved and `git diff --check` passed.
- Graphify was regenerated and source-fingerprint stamped.
- The authorized `.DS_Store` cleanup is recoverable from macOS Trash.
- The in-image boundary proof could not run locally because no Docker application/daemon exists; CI now performs it after image construction.
- The public remote is `vaibhavkhuranaaa/text-to-sql-guardrails`; the exact source commit and replacement deployment are anonymously verifiable. The current branch is `main`.

## No-expiry transition

- Expiry configuration, runtime refusal/status fields, workflow inputs, and deployment-evidence fields were removed. Anonymous access remains intentionally login-free and non-production.
- Local format/lint, 29 tests, evaluation, live-profile manifest validation, Compose configuration, presentation validation, and `git diff --check` passed.
- The local Docker daemon is unavailable; CI remains responsible for the in-image boundary proof.
- After the change reaches `main`, use the release workflow’s exact-SHA receipt to refresh `evidence/deployment/anonymous-live-demo.json`. Do not claim the new no-expiry revision is live until that receipt is available.
- Regenerate Graphify after the authoritative revision is committed; the current graph predates this transition.

## Later protected-hosting gate

Use single-tenant Microsoft Entra authentication, an owner-approved transactional proposal store, verified cross-replica single-use behavior, monitoring and alerting, and an owner-approved cost/load envelope before protected hosting. Publication does not convert this anonymous live demo into a production service.

## Checkpoint 2026-07-24T05:30:15.531Z

Presentation handoff completed for text-to-sql-guardrails.

- `sh -lc uv run ruff format --check . && uv run ruff check .` passed in 146 ms.
- `sh -lc uv run pytest -q` passed in 877 ms.
- `sh -lc uv run python scripts/run_evaluation.py && uv run python scripts/validate_manifest.py` passed in 358 ms.
- `sh -lc docker compose config >/dev/null` passed in 125 ms.
- `node scripts/project-presentation.mjs validate --check` passed in 36 ms.
- `sh -lc ! rg -n '(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----)' --glob '!uv.lock' --glob '!package-lock.json' .` passed in 96 ms.
- `git diff --check` passed in 10 ms.

Public membership and exact-SHA approval were not changed.

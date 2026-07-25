# Deployment

The release workflow records status-only verification for the root, evaluation, examples, safe preview, fixture boundary, and anonymous-demo controls in `evidence/deployment/anonymous-live-demo.json`. A replacement revision must report its exact source SHA before the evidence record is refreshed.

The anonymous portfolio demo is live at `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io` on Container App revision `ca-text-sql-guardrails-dev--0000007`. It uses image `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:6ba0f20` (digest `sha256:fb11bdf14321e18fb835670154b737a3d4ff6d81c5c29ebba4f79c9c47bc7e53`). The exact Azure-built image passed the in-image boundary verifier; public route and fixture checks passed against the replacement revision.

This is deliberately anonymous: Container Apps auth is disabled and `AllowAnonymous` remains configured. Anyone with the URL can send Foundry-backed questions and approve their own bounded preview. There is no caller identity, analyst authorization, availability/SLO evidence, or production monitoring claim. Do not describe this deployment as secure or production-ready.

The anonymous live revision exposes a five-proposal-per-minute gate, a 100-proposal per-process budget, and aggregate status counters. These are process-local controls, not distributed authorization or a durable budget: they reset after scale-to-zero or restart. The demo has no automatic expiry; the workspace owner remains responsible for ongoing cost and operational review.

The app scales from zero to one replica and stores pending approvals at `/tmp/text-to-sql-guardrails-proposals.sqlite3`. Approvals are single-use and expire after five minutes, but disappear after scale-to-zero, restart, or a revision change. The Azure Files mount remains provisioned but is not used for SQLite: fresh database paths on that mount returned `sqlite3.OperationalError: database is locked`. Revision `ca-text-sql-guardrails-dev--0000006` is the immediate application rollback revision.

The status-only M6 operational procedure is in `docs/m6-operational-runbook.md`.
Its bounded $30 monthly budget, redacted owner notification route, and
aggregate stderr/latency alerts are recorded in
`evidence/m6/operational-observation.json`. They do not add an on-call,
availability target, or production-monitoring claim.

Before any protected or multi-replica hosting, replace SQLite with an owner-approved transactional store, enable single-tenant Microsoft Entra authentication, verify unauthenticated denial, and add alerting plus budget/availability evidence. `infra/main.bicep` remains a future-only reference and was not used for this deployment.

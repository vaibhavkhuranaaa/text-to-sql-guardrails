# Deployment

Current status-only verification (2026-07-24T04:25:22Z): the root, evaluation, examples, safe preview, fixture-boundary, and anonymous-demo-control checks passed. The record is `evidence/deployment/temporary-demo.json`.

The anonymous portfolio demo is live at `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io` on Container App revision `ca-text-sql-guardrails-dev--0000007`. It uses image `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:6ba0f20` (digest `sha256:fb11bdf14321e18fb835670154b737a3d4ff6d81c5c29ebba4f79c9c47bc7e53`). The exact Azure-built image passed the in-image boundary verifier; public route and fixture checks passed against the replacement revision.

This is deliberately anonymous: Container Apps auth is disabled and `AllowAnonymous` remains configured. Anyone with the URL can send Foundry-backed questions and approve their own bounded preview. There is no caller identity, analyst authorization, production monitoring, or availability/SLO evidence. Do not describe this deployment as secure or production-ready.

The current revision exposes and passed verification for a five-proposal-per-minute gate, a 100-proposal per-process budget, aggregate status counters, and application expiry. These are process-local controls, not distributed authorization or a durable budget: they reset after scale-to-zero or restart. The external demo has an owner-controlled expiry of `2026-08-06T23:59:59Z`; the workspace owner is responsible for disabling ingress or deleting the resource. The application cannot tear down Azure infrastructure.

The app scales from zero to one replica and stores pending approvals at `/tmp/text-to-sql-guardrails-proposals.sqlite3`. Approvals are single-use and expire after five minutes, but disappear after scale-to-zero, restart, or a revision change. The Azure Files mount remains provisioned but is not used for SQLite: fresh database paths on that mount returned `sqlite3.OperationalError: database is locked`. Revision `ca-text-sql-guardrails-dev--0000006` is the immediate application rollback revision.

Before any protected or multi-replica hosting, replace SQLite with an owner-approved transactional store, enable single-tenant Microsoft Entra authentication, verify unauthenticated denial, and add alerting plus budget/availability evidence. `infra/main.bicep` remains a future-only reference and was not used for this deployment.

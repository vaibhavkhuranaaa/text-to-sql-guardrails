# Deployment

Current status-only verification (2026-07-23T20:43:49Z): the root, evaluation, examples, safe preview, and fixture-boundary routes returned successful responses. The record is `evidence/deployment/temporary-demo.json`.

The anonymous portfolio demo is live at `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io` on Container App revision `ca-text-sql-guardrails-dev--0000006`. It uses image `textsqlguardrails278f1d.azurecr.io/text-to-sql-guardrails:20260723-3` (digest `sha256:9ea98f96e2f23f84d50c148c3699c65205db66a4076e412b0ead001d94923cc7`). The public root, evaluation report, schema-matched examples, safe fixture preview, and one proposal-to-approved-execution lifecycle were verified on 2026-07-23; a second approval was refused.

This is deliberately anonymous: Container Apps auth is disabled and `AllowAnonymous` remains configured. Anyone with the URL can send Foundry-backed questions and approve their own bounded preview. There is no caller identity, analyst authorization, production monitoring, or availability/SLO evidence. Do not describe this deployment as secure or production-ready.

The current revision predates the source-level proposal rate limit, per-process proposal budget, aggregate status counters, and application expiry. Those controls are verified only in source/tests until a replacement revision is owner-authorized and deployed. The external demo has an owner-controlled expiry of `2026-08-06T23:59:59Z`; the workspace owner is responsible for disabling ingress or deleting the resource. The application cannot tear down Azure infrastructure.

The app runs exactly one replica and stores pending approvals at `/tmp/text-to-sql-guardrails-proposals.sqlite3`. Approvals are single-use and expire after five minutes, but disappear after restart, scaling, or a revision change. The Azure Files mount remains provisioned but is not used for SQLite: fresh database paths on that mount returned `sqlite3.OperationalError: database is locked`. The previous revision `ca-text-sql-guardrails-dev--0000005` remains the rollback revision, but it retains that Azure Files SQLite limitation.

Before any protected or scaled hosting, replace SQLite with an owner-approved transactional store, enable single-tenant Microsoft Entra authentication, verify unauthenticated denial, deploy and verify the source-level limits, and add alerting plus budget/availability evidence. `infra/main.bicep` remains a future-only reference and was not used for this deployment.

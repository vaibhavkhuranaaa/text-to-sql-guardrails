# Handoff

## Start here

Read `AGENTS.md`, `docs/STATE.md`, this file, `docs/scale-ready-milestones.md`, `portfolio/project.json`, and the relevant fresh `graphify-out/` query before broad inspection. Current `main` is `6c6cd48bd9e6faf802369338a6e2fe47c9333e79`; `docs/STATE.md` separately records the deployed, verified source SHA.

The demo is live, anonymous, indefinite, non-production, scale-to-zero, and backed only by the committed hand-authored synthetic fixture. Do not add login, caller authorization, real customer data, raw data to the image, a public database endpoint, or a production/SLA claim.

## Current direction

This is a cost-first evidence plan, not a productionization plan. The default is to keep one Container App replica and the existing ephemeral SQLite approval store. That limitation must remain disclosed.

If the owner requests a two-replica or restart-persistence proof, the proposed first durable store is Azure Table Storage with managed identity and ETag conditional operations. PostgreSQL is deferred for measured relational/transactional needs; do not provision either store without explicit approval.

## M0 outcome

The owner selected M0-A: retain the one-replica SQLite demo and do not add a
new Azure resource or incremental monthly-cost envelope. Aggregate-only
baseline evidence is in `evidence/m0/baseline.json`. The IBM acquisition
procedure in `docs/ibm-aml-acquisition.md` is approved, but no data download is
authorized until M3.

## Active milestone

**M1 — Low-cost proposal-path controls** in `docs/scale-ready-milestones.md`.

Keep the public demo anonymous, scale-to-zero, and at one replica. The working
tree adds aggregate-only, process-local proposal telemetry at `/v1/status`:
proposal outcomes, provider-call counts, provider-reported token totals, and
fixed latency buckets. Lifecycle logs are sampled status-only metadata with no
identifiers or configured exporter. Observe an aggregate window before deciding
whether to tighten the existing five-per-minute and 100-per-process limits.
Do not provision Azure resources, alter capacity, download IBM data, add login,
or edit Resume Creator.

## Required verification

For every implementation milestone run formatting, lint, tests, evaluation generation, manifest validation, Docker Compose validation, the container data-boundary check, and `git diff --check`, plus the milestone-specific checks defined in the plan.

## Resume prompt

> Continue the Text-to-SQL Guardrails cost-first scale-ready evidence plan in `docs/scale-ready-milestones.md`. Read `AGENTS.md`, `docs/STATE.md`, `docs/HANDOFF.md`, this plan, `portfolio/project.json`, and fresh Graphify context first. Preserve the anonymous, indefinite, non-production Azure demo and its committed synthetic public fixture. Do not provision resources, download IBM data, change deployment capacity, add login, or edit Resume Creator without the exact owner approval required by the active milestone. Report the active milestone, unresolved gates, evidence, and the next safe action before implementation.

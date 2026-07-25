# Handoff

## Start here

Read `AGENTS.md`, `docs/STATE.md`, this file, `docs/scale-ready-milestones.md`, `portfolio/project.json`, and the relevant fresh `graphify-out/` query before broad inspection. The last independently live-verified application release is `36156cc825c0245e0bf803c2aeb75718998d7126` (workflow `30177660324`).

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

## M1 deployment evidence

M1 telemetry merged and deployed in `397b42666f3d999e33e66b0e7eae413b2f9569fa`.
Release workflow `30145269339` passed its exact-SHA, required-check,
container-boundary, immutable-image, deployment, and live-verification gates.
The row-free, aggregate-only status observation is recorded in
`evidence/m1/deployment-observation.json`.

It observed zero post-deployment proposal traffic, so it confirms the telemetry
contract and existing five-per-minute / 100-per-process envelope but provides no
evidence for changing either limit. Retain both limits unless separately
authorized.

## M3 private benchmark evidence

The owner authorized the pinned IBM version-8 acquisition. The local raw files,
identifier-free DuckDB derivative, and row-free benchmark report are ignored by
Git and container builds. `data/ibm_aml_manifest.json` pins version, license,
byte counts, and SHA-256 digests; `scripts/build_ibm_aml_benchmark.py` verifies
them and creates the seven-field private derivative without account or bank
fields. The derivative uses a deterministic curated-content digest for
repeatability. Keep the 30-day local retention/deletion policy in effect.

M2 is skipped under M0-A. M4 merged and deployed as
`05cfcdf79c1cebfdd000a5c1955ed698157eba81`; workflow `30146749371` verified
that exact SHA on the existing target. Its ignored aggregate-only private report
passed seven reviewed aggregate/resource-boundary checks. The row-free live
status observation in `evidence/m4/deployment-observation.json` has zero
aggregate traffic/model calls and leaves the five-per-minute / 100-per-process
limits unchanged.

M5's bounded local and four-call provider evidence is complete. Do not claim a
full load envelope or run additional provider, public-load, durable-contention,
or scaling work. Do not provision resources, alter capacity, add login, or edit
Resume Creator.

## Completed M5 evidence

The bounded provider cap release merged as `64aa8248467c0baf505b109d58031833bd8a85aa`
and deployed successfully. The fixed cap is 2,048 completion tokens. A private
four-call sample recorded only aggregate outcomes: 4 valid proposals, 760 input
tokens, 4,685 output tokens, and 25,079 ms observed p95 latency.
`scripts/run_bounded_provider_m5.py` is the fixed four-call aggregate-only
reproduction harness; it writes only an ignored local report and must not be
rerun without confirming the approved optional-test cost threshold.

`scripts/run_private_m5_readiness.py` is the versioned source for an ignored,
aggregate-only local report. Its default no-provider run passed seven
private-volume checks; across 12 deterministic service requests at three workers
it recorded six trusted and six refused outcomes. The same run reproduced one
policy refusal, one approved execution, one expiry refusal, and two concurrent
approval attempts with zero duplicate executions. It explicitly records that
durable-store contention is non-applicable to the M0-A ephemeral SQLite demo
and scaling remains unexercised at zero-to-one replica. This is not a public
load envelope or performance/cost claim. Keep the $24 optional-test stop
threshold.

The versioned redacted aggregate report is
`evidence/m5/aggregate-readiness.json`. It combines the recorded provider
totals, local readiness outcomes, container-boundary result, and explicit M0-A
caveats without raw prompts, SQL, rows, identifiers, per-request tokens, source
rows, or environment values. It does not calculate provider monetary cost: no
verified unit price or portal-cost observation is retained.

M6 is complete as bounded operational evidence. The existing target now has a
redacted owner notification route, $30 monthly budget thresholds, and enabled
five-minute aggregate stderr and latency alerts. The retained observation is
`evidence/m6/operational-observation.json`; it creates no production SLO,
on-call, durable-state, or public-load claim.

The required local built-container data-boundary check passed against
`text-to-sql-m5-check`: the fixture and aggregate evaluation evidence were
present, while raw and approved artifacts were absent.

M5 is complete as a bounded private evidence milestone. M6 is also complete
within its stated non-production operational scope. M7 consumer convergence is
active with the owner's explicit Resume Creator synchronization approval; do
not infer approval for durable state, scaling, public load, capacity, or login.

## M6 operational evidence

The M6 configuration is deployed on the existing non-production target: enabled
action group `ag-text-sql-m6-owner`, a $30 monthly budget with $15 actual, $24
forecast, and $30 actual thresholds, plus enabled five-minute aggregate stderr
and latency scheduled-query alerts. The owner confirmed the notification
receipt; `evidence/m6/operational-observation.json` retains only redacted,
aggregate configuration evidence.

`docs/m6-operational-runbook.md` and
`scripts/verify_m6_operational_readiness.py` cover status-only health,
process-local telemetry, degraded SQLite behavior, rollback, and the M0-A
non-applicable durable-state restore drill. No capacity, durable state, login,
public load, availability target, on-call rota, or production claim was added.

## Completed M7 consumer convergence

The owner explicitly authorized Resume Creator synchronization. Portfolio Site
re-verified and projected source SHA
`64aa8248467c0baf505b109d58031833bd8a85aa`; Resume Creator imported that
approved catalog and refreshed only the matching evidence-backed reviewed
references. Portfolio Site tests, lint, and build passed; Resume Creator catalog
validation, six tests, lint, and build passed; and Portfolio OS reported no
cross-consumer mismatch. Its generated GitHub index carries the same SHA.

M7 is complete. This synchronizes only already live-verified M5-era public
facts; the local M6 observation remains versioned evidence pending a future
normal source release and does not create a new public performance, cost, or
production claim.

## Required verification

For every implementation milestone run formatting, lint, tests, evaluation generation, manifest validation, Docker Compose validation, the container data-boundary check, and `git diff --check`, plus the milestone-specific checks defined in the plan.

## Resume prompt

> Continue the Text-to-SQL Guardrails cost-first scale-ready evidence plan in `docs/scale-ready-milestones.md`. Read `AGENTS.md`, `docs/STATE.md`, `docs/HANDOFF.md`, this plan, `portfolio/project.json`, and fresh Graphify context first. Preserve the anonymous, indefinite, non-production Azure demo and its committed synthetic public fixture. Do not provision resources, download IBM data, change deployment capacity, add login, or edit Resume Creator without the exact owner approval required by the active milestone. Report the active milestone, unresolved gates, evidence, and the next safe action before implementation.

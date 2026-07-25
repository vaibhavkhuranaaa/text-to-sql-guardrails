# Cost-first scale-ready evidence plan

## Purpose and authority

This is the authoritative plan for the next milestone sequence. It is intentionally a portfolio-evidence plan, not a production launch plan. `docs/STATE.md` records what is true now; `docs/HANDOFF.md` is the concise continuation checklist; this document provides the detailed scope and gates.

## Invariants: do not change without separate owner approval

- The existing Azure Container App remains the only application host and stays anonymous, indefinite, non-production, and scale-to-zero.
- The committed six-field hand-authored synthetic fixture remains the only public/live dataset.
- No end-user login, caller authorization boundary, real customer data, bank-system claim, availability SLO, or 24/7 on-call program is added.
- Azure OpenAI remains proposal-only through managed identity. SQLGlot policy, DuckDB `EXPLAIN`, explicit approval, snapshot revalidation, read-only execution, and bounded previews remain mandatory.
- Raw analyst questions, result rows, source rows, source identifiers, tokens, and environment values are never logged or published.
- Raw or approved benchmark artifacts remain ignored by Git and excluded from the container image.
- Resume Creator is not edited or synchronized until its independent consumer workflow is explicitly authorized.

## Cost and architecture decision

### Default: keep the public demo single-replica

Keep `minReplicas=0` and `maxReplicas=1`; retain ephemeral SQLite approval state and process-local proposal limits. This is the lowest-cost topology and accurately preserves the demo's current limitations. It is acceptable while no cross-replica or restart-persistence claim is made.

### Optional durable-state path: Azure Table Storage first

This path requires owner approval and is selected only if a two-instance/restart-persistence proof is required.

- One Standard, LRS StorageV2 account with Table Storage; no benchmark data in that account.
- Managed identity and RBAC only; shared-key access disabled, public blob access disabled, HTTPS/TLS required.
- A pending approval is one entity containing only its UUID, approval-token hash, validated canonical SQL/revalidation metadata, snapshot digest, policy version, trace ID, and five-minute expiry.
- Consume an approval through ETag-conditional delete; consume it before SQL execution.
- Use daily-rotated HMAC-derived requester keys and conditional counter updates for low-volume, privacy-preserving limits. Do not store raw IP addresses or treat a key as identity/authorization.
- Clean up expired entities during normal reads/writes and bounded maintenance; do not create an always-on worker just for expiry.

### PostgreSQL is an escalation, not the default

Azure Database for PostgreSQL Flexible Server is considered only after owner approval when one or more of these are true: relational operational reporting is needed, contention makes ETag retries unsuitable, transactional relationships span multiple entities, or state must live longer than the short approval/quota windows. It must not be provisioned merely to make the portfolio demo appear more enterprise-like.

### Provisional cost policy — not approved

- Proposed incremental ceiling: **$30/month**, excluding already-running Container App and existing Azure OpenAI deployment.
- Alert thresholds if a paid resource is approved: $15, $24, and $30; stop optional load testing at $24.
- IBM benchmark storage: local, ignored, private only; no Azure storage cost is planned.
- Azure OpenAI test budget: bounded before each test run by a request/token envelope and checked against observed portal usage; no invented unit-cost claim.
- Budgets alert; they do not technically prevent spend. Any resource choice needs a fresh regional quote at approval time.

## Milestones

### M0 — Baseline and owner decisions

**Goal:** establish evidence and approvals without changing cloud resources or acquiring IBM data.

- Record a clean baseline for model-call count, proposal refusals, latency buckets, and existing process budget using aggregate-only telemetry.
- Confirm whether the goal is (A) lowest-cost single-replica evidence or (B) durable two-replica/restart evidence.
- If B, approve the Table Storage resource/configuration and managed-identity/RBAC plan; document the networking/authentication compatibility check before provisioning.
- Confirm the $30 provisional ceiling or replace it with an owner-selected limit.
- Pin an immutable IBM artifact release, provider URL, file names, provider version/revision, and acquisition checklist. Do not download in this milestone.

**Exit:** owner selects A or B, approves any paid-resource envelope, and approves the acquisition procedure. No resources or data change before this exit.

### M1 — Low-cost proposal-path controls

**Goal:** reduce variable Azure OpenAI and telemetry cost while preserving safety.

- Measure proposal input/output token and request envelopes using aggregate counts only.
- Keep the model context to the identifier-excluding semantic catalog, fixed policy, and bounded output contract; do not send fixture rows or broad examples.
- Set the smallest useful anonymous proposal budget and request length after baseline evidence; retain refusal behavior before any model call when deterministic policy can reject.
- Configure status-only, sampled telemetry and a documented retention boundary.

**Exit:** tests show the same safety behavior; aggregate evidence shows the chosen budget/envelope; no public raw request or response content is retained.

### M2 — Durable state, only if M0 selected option B

**Goal:** prove cross-replica one-time approval and durable quota behavior at the lowest justified standing cost.

- Introduce a storage interface; preserve SQLite for local tests and the M0-A demo path.
- Implement the Table Storage adapter with ETag conditional operations, five-minute approval expiry, privacy-preserving quota keys, and fail-closed store errors.
- Prove two concurrent services cannot execute the same approval twice; prove restart persistence and expired-row cleanup.
- Keep the application at the existing hosting target; do not add Redis, Front Door/WAF, API Management, a new Container Apps environment, or login.

**Exit:** concurrency, restart, retention, and failure-mode tests pass; documentation identifies only aggregate status evidence.

**Fallback:** if measured contention or data-model needs invalidate Table Storage, stop and request a separate PostgreSQL escalation decision. Do not silently substitute PostgreSQL.

### M3 — Private IBM synthetic AML benchmark acquisition and build

**Goal:** build a repeatable private benchmark without widening the public data boundary.

- Download only after M0 approval, verify every acquired artifact against its recorded checksum, and retain license/provenance metadata.
- Keep raw source files, account-like identifiers, and laundering labels outside model context, public previews, logs, container context, and public evidence.
- Produce an ignored private Parquet/DuckDB derivative containing only approved analytical fields.
- Record only benchmark digest, row count, schema/transform version, and aggregate outcomes.
- Apply the 30-day local retention/deletion policy to raw and derived benchmark artifacts; retain row-free provenance/evidence metadata.

**Exit:** checksum, license, field-boundary, container-boundary, and repeatable-build checks pass.

### M4 — Stronger correctness and safety evaluation

**Goal:** replace a narrow case set with reviewed aggregate evidence.

- Cover aggregation, joins, time windows, nulls, currencies, unknown schema, identifier attempts, prompt injection, malformed SQL, and resource limits.
- Compare semantic execution results to approved expected aggregates rather than relying only on literal SQL equality.
- Publish only model/version, dataset digest, case counts, aggregate pass/fail counts, thresholds, and limitations.

**Exit:** generated report is reproducible and contains no raw prompts, SQL, rows, source values, tokens, or environment values.

### M5 — Bounded private scale validation

**Goal:** establish an evidence-backed—not invented—load envelope.

- Test data volume on the private benchmark separately from concurrent service load.
- Use a bounded mix of safe proposals, refusals, approvals, expiry attempts, and durable-store contention.
- Stop on the M0 cost threshold; never run an unbounded public load test.
- Measure aggregate p50/p95/p99 latency, throughput, error/refusal rates, duplicate-execution count, durable-store contention, scaling observations, and model-token/cost totals.

**Exit:** reproducible load script and redacted aggregate report establish a documented envelope with caveats.

### M6 — Lean operational evidence

**Goal:** add recovery evidence without an on-call/SLA commitment.

- Add approved budget alerts, health/error/latency monitoring, and one named owner notification route.
- Document rollback, degraded-store behavior, and restore/recovery steps appropriate to the selected durable-state path.
- Perform one restore or state-recovery drill only after the relevant resource is approved.

**Exit:** alert receipt, drill receipt, runbook, and failure-mode tests pass; non-production/no-SLA disclosure remains intact.

### M7 — Evidence publication and consumer convergence

**Goal:** publish only verified aggregate claims and synchronize consumers deliberately.

- Update portfolio facts only when each claim has a versioned evidence ID.
- Obtain explicit approval before triggering Resume Creator's independent catalog synchronization.
- Verify Portfolio Site, Resume Creator, and Portfolio OS carry the same source SHA after synchronization.

**Exit:** the consumer validation passes with no source-SHA mismatch.

## Verification matrix

Every implementation milestone runs the existing required checks: formatting, lint, tests, evaluation generation, manifest validation, Docker Compose validation, container data-boundary verification, and `git diff --check`. Add focused tests for the selected milestone: storage concurrency/restart/retention, private-data boundary, evaluation, bounded load, or recovery drill.

## Resume prompt

> Continue the Text-to-SQL Guardrails cost-first scale-ready evidence plan in `docs/scale-ready-milestones.md`. Read `AGENTS.md`, `docs/STATE.md`, `docs/HANDOFF.md`, this plan, `portfolio/project.json`, and fresh Graphify context first. Preserve the anonymous, indefinite, non-production Azure demo and its committed synthetic public fixture. Do not provision resources, download IBM data, change deployment capacity, add login, or edit Resume Creator without the exact owner approval required by the active milestone. Report the active milestone, unresolved gates, evidence, and the next safe action before implementation.

# Handoff

## Start here

Read `AGENTS.md`, `docs/STATE.md`, this file, `portfolio/project.json`, and the relevant fresh `graphify-out/` query before broad inspection. The current source of truth is `main` at `c6e8441e401efe6c9214b8231e932c7dc6c1467e`.

The existing demo is live, anonymous, indefinite, and non-production. Do not add end-user login, caller authorization, real customer data, raw data to the image, or a production/SLA claim.

## Objective

Deliver a scale-ready portfolio evidence milestone without turning the service into a production banking or AML decision system:

1. make proposal state and baseline quota enforcement durable across restart and replicas;
2. evaluate safely against a larger, licensed IBM synthetic AML corpus kept outside the public image;
3. prove the controls under a documented data-volume and concurrent-load envelope;
4. add lean recovery evidence, not a 24/7 on-call program; and
5. synchronize Resume Creator only after its independent consumer workflow is deliberately included.

## Milestones and decision gates

### 0. Design, data, and cost gate

- Confirm the exact IBM AML dataset release, CDLA-Sharing-1.0 obligations, checksum, retention policy, field classification, and permitted evaluation use before downloading it.
- Define a monthly cost ceiling and region for one Azure Database for PostgreSQL Flexible Server instance, backup retention, observability ingestion, benchmark storage, and Azure OpenAI load-test tokens.
- Confirm the existing Container App remains the only hosting target. PostgreSQL is a new paid resource and requires explicit owner approval before provisioning.

**Exit:** an approved architecture decision record and cost envelope. No resource or data change before this exit.

### 1. Durable approval and quota state

- Introduce a storage abstraction; retain SQLite only for local tests and demo fallback.
- Implement PostgreSQL-backed pending proposals with an atomic compare-and-consume operation, five-minute TTL cleanup, and no stored raw questions/result rows.
- Store only the approval-token hash, proposal metadata required for revalidation, and privacy-safe aggregate counters.
- Implement durable global proposal budget plus a privacy-preserving, windowed requester key. Treat anonymous IP-derived limits as abuse mitigation, not identity or authorization.
- Prove single-use approval across at least two service instances and prove restart persistence.

**Exit:** migration tests, concurrency tests, restart tests, schema/retention documentation, and aggregate status evidence pass.

### 2. Private IBM benchmark pipeline

- Preserve the six-field committed fixture as the only public/live dataset.
- Add a separate ignored ingestion path that verifies IBM source checksum and license metadata, classifies all fields, and produces an approved private Parquet/DuckDB benchmark snapshot.
- Exclude account-like identifiers, laundering labels, and raw source rows from model context, public previews, logs, and container build context unless a documented safe aggregate use is approved.
- Record row count, schema version, transformation version, and benchmark digest only; never publish source rows.

**Exit:** provenance, field-boundary tests, container-boundary test, and repeatable private build pass.

### 3. Stronger correctness and safety evaluation

- Expand from 18 deterministic cases to a reviewed matrix covering aggregation, joins, time windows, nulls, currencies, unknown schema, identifier attempts, prompt injection, malformed SQL, and resource-limit cases.
- Score semantic execution equivalence against approved expected aggregates rather than literal SQL strings alone.
- Keep model/version, dataset digest, test counts, and aggregate outcomes; do not retain raw questions, SQL, result rows, tokens, or environment values in public evidence.

**Exit:** generated evaluation report identifies scope, dataset digest, thresholds, pass/fail counts, and limitations.

### 4. Scale validation

- Test two axes separately: data volume on the private IBM benchmark and concurrent request load against the service.
- Use a bounded load mix of safe proposals, refusals, approvals, expiry attempts, and durable-store contention; do not run an unbounded public load test.
- Measure aggregate p50/p95/p99 latency, throughput, error/refusal rates, duplicate-execution count, database contention, Container Apps scaling behavior, and Azure OpenAI token/cost totals.
- Set the actual load envelope only after a baseline; publish measurements and caveats, not an invented capacity claim.

**Exit:** reproducible load script, redacted aggregate report, and evidence-backed portfolio wording.

### 5. Lean operational evidence

- Add Azure budget alerting, service health/error/latency monitoring, and one named owner notification route.
- Document rollback, database restore, and degraded-store behavior; perform one restore drill.
- Keep the non-production/no-SLA disclosure. Do not create a 24/7 on-call commitment.

**Exit:** alert receipt, restore-drill receipt, runbook, and failure-mode tests pass.

### 6. Consumer convergence

- Trigger Resume Creator's independent approved-catalog synchronization after the source manifest/evidence are finalized.
- Verify Portfolio Site, Resume Creator, and Portfolio OS report the same exact source SHA.

**Exit:** `npm run validate:consumers` in Portfolio OS passes with no source-SHA mismatch.

## Stack decision

Start with Azure Database for PostgreSQL Flexible Server for durable approval state and low-volume durable counters. Add Azure Front Door WAF and Redis only if measured scale tests show that PostgreSQL counters or direct anonymous ingress are the limiting control. This avoids paying for a larger edge/cache platform before evidence warrants it.

## Required verification

Run the existing project checks plus focused migration, concurrency, private-data-boundary, evaluation, load, and restore checks. Then run Portfolio Site synchronization and Portfolio OS consumer validation. Refresh Graphify and stamp its source fingerprint only after the implementation and handoff stabilize.

## Resume prompt

> Continue the Text-to-SQL Guardrails scale-ready evidence milestone from `docs/HANDOFF.md`. Read `AGENTS.md`, `docs/STATE.md`, the handoff, `portfolio/project.json`, and fresh Graphify context first. Preserve the anonymous, indefinite, non-production Azure demo and its synthetic public fixture. Start at Milestone 0: produce an architecture/cost/data-governance decision record for PostgreSQL-first durable approval/quota state and an IBM synthetic AML private benchmark. Do not provision Azure resources, download IBM data, change deployment capacity, add user login, or edit Resume Creator without explicit owner approval. Return the decision record and exact cost/resource choices for approval before implementation.

# State

## Delivered state

- Lifecycle: `maintained` portfolio project.
- Deployment: anonymous, indefinite, non-production `live` demo on the existing Azure Container App.
- Last independently live-verified application release: `c5024f82af435805c3411344bab0bcbd8fa34378` on `main`.
- Deployment verification: GitHub Actions workflow `30222770159` deployed and verified that exact release SHA.
- Portfolio publication: the public site verified and synchronized the project; its tracked catalog now records the same source SHA.
- Public endpoint: `https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io`.

The demo has no end-user login. Azure managed identity is used only for the service-to-Azure OpenAI call. It remains explicitly non-production and uses the committed hand-authored synthetic fixture only.

## Implemented controls and evidence

- Azure OpenAI proposals are separated from execution; SQLGlot policy, DuckDB `EXPLAIN`, read-only execution, bounded previews, and explicit human approval remain required.
- Approval tokens are five-minute and single-use; SQL policy and fixture checksum are revalidated before execution.
- The live release passed exact-SHA, image-digest, fixture-boundary, and no-expiry status verification.
- Local deterministic evaluation recorded 18 of 18 expected trusted or refused outcomes.
- The container boundary excludes raw source data and approved snapshots from the image.
- Required local checks and the release workflow were green for the permanent-demo change.

## Known, intentional limitations

- Proposal-rate and total-proposal controls are process-local; they reset after restart or scale-to-zero.
- SQLite proposal state lives under `/tmp`; it cannot safely coordinate replicas and is lost on restart.
- The public fixture is intentionally small. The ignored local approved snapshot is never deployed.
- There is no availability SLO, on-call rota, production authorization boundary, or real-customer data claim.
- M7 consumer convergence passed. Portfolio Site, its generated GitHub index,
  and Resume Creator all carry the live-verified source SHA
  `c5024f82af435805c3411344bab0bcbd8fa34378`; Portfolio OS's consumer validator
  reported no mismatch.

## M0 outcome

- The owner selected M0-A: retain the zero-to-one-replica public demo and its
  ephemeral SQLite state; no new Azure resource or incremental monthly-cost
  envelope is authorized.
- The owner approved the IBM artifact-pinning procedure in
  `docs/ibm-aml-acquisition.md`; it does not authorize a dataset download.
- Aggregate-only baseline evidence is recorded in `evidence/m0/baseline.json`.

## M1 deployment observation

- The M1 telemetry release merged as `397b42666f3d999e33e66b0e7eae413b2f9569fa`
  and GitHub Actions workflow `30145269339` deployed and live-verified that
  exact SHA on the existing Azure target.
- It adds process-local aggregate proposal telemetry at `/v1/status`: proposal
  outcomes, provider-call counts, provider-reported token totals, and fixed
  latency buckets. Lifecycle logs are sampled status-only metadata with no
  identifiers or configured exporter.
- The one bounded status observation is recorded in
  `evidence/m1/deployment-observation.json`. It captured zero aggregate proposal
  traffic after deployment, so the existing five-per-minute and 100-per-process
  limits remain unchanged. It is not a production cost or performance claim.
- Verification passed: formatting, lint, 31 tests, deterministic evaluation
  generation, manifest validation, presentation validation, Docker Compose,
  `git diff --check`, and the built-container data-boundary verification.

## M3 private IBM benchmark

- The owner authorized the pinned version-8 IBM AML artifact acquisition.
- The two approved artifacts are checksum-locked in `data/ibm_aml_manifest.json`.
  Raw files, the identifier-free private DuckDB derivative, and row-free local
  benchmark evidence remain ignored by Git and excluded from container builds.
- The private derivative excludes account and bank fields, retains only approved
  analytical fields, and uses a deterministic curated-content digest for
  repeatable-build verification. The raw and derived artifacts are subject to
  the documented 30-day local retention/deletion policy.

## M4 private semantic evaluation

- M4 merged as `05cfcdf79c1cebfdd000a5c1955ed698157eba81` and the existing Azure
  target live-verified that exact release SHA in workflow `30146749371`.
- It adds a private, ignored aggregate-only evaluator. It compares reviewed
  aggregate semantics across aggregation, joins,
  time windows, null handling, currencies, labels, and existing resource bounds.
- The generated report contains only the deterministic curated-content digest,
  case/pass/fail counts, threshold, limitations, and disclosure. It never enters
  the image, public demo, logs, or public evidence.
- The local M4 evaluation passed all seven checks. The bounded aggregate-only
  deployment observation is recorded in `evidence/m4/deployment-observation.json`;
  it retains the existing five-per-minute and 100-per-process limits unchanged.
- M6 and M7 are complete within their documented bounded scope.

## Next safe action

M2 is skipped under M0-A, and M4 through M7 are complete only within their
documented bounded evidence scope. No further provider, public-load,
durable-store, or scaling work is authorized. Retain the existing proposal
limits unless the owner separately authorizes a policy change.

## M5 bounded private provider sample

- The owner approved the documented $30 incremental ceiling and $24 optional-test
  stop threshold; no new resource or capacity is authorized.
- Provider completions are capped at 2,048 tokens. Four isolated private calls
  produced valid guarded proposals; aggregate usage was 760 input and 4,685
  output tokens with observed p95 latency of 25,079 ms. The fixed four-call,
  aggregate-only reproduction harness is `scripts/run_bounded_provider_m5.py`;
  it must not be rerun without confirming the optional-test cost threshold.
- The versioned local readiness harness now writes an ignored, aggregate-only
  report. Its default no-provider run passed seven private-volume checks and
  exercised 12 deterministic service requests at three workers, with six
  trusted and six refused outcomes. It also reproduced one policy refusal, one
  approved execution, one expiry refusal, and two simultaneous approval
  attempts with zero duplicate executions.
- This remains a bounded M5 slice, not a full load envelope: durable-store
  contention is non-applicable to M0-A's ephemeral SQLite demo, scaling remains
  unexercised at zero-to-one replica, and the local observation is not a public
  performance or cost claim. M6 remains separately owner-gated.
- The required local built-container data-boundary recheck passed: the fixture
  and aggregate evaluation evidence were present, while raw and approved
  artifacts were absent.
- The versioned, redacted aggregate report is
  `evidence/m5/aggregate-readiness.json`. It records only aggregate provider,
  local-readiness, container-boundary, and caveat evidence; provider monetary
  cost is deliberately not calculated without a verified portal observation or
  unit price.
- M5 is complete as a bounded, private evidence milestone. It does not justify
  a public-load, durable-state, scaling, production-performance, or monetary
  cost claim. M6 remains separately owner-gated.

## M6 operational evidence

- The owner authorized the redacted notification route and confirmed its receipt.
  The existing target now has enabled action group `ag-text-sql-m6-owner`, the
  `text-sql-m6-monthly` $30 monthly budget ($15 actual, $24 forecast optional
  test stop, and $30 actual), plus enabled five-minute aggregate stderr and
  latency scheduled-query alerts.
- `docs/m6-operational-runbook.md` and
  `scripts/verify_m6_operational_readiness.py` document and verify the
  status-only health observation, process-local telemetry limitation,
  degraded-proposal-store behavior, rollback procedure, and M0-A's
  non-applicable durable-state restore drill.
- `evidence/m6/operational-observation.json` is redacted aggregate-only
  configuration evidence. M6 adds no capacity, durable state, login, public
  load, availability target, on-call rota, or production claim.

No new Azure resource, paid capacity, raw IBM data download, capacity change,
or user login is authorized. The default remains one replica with ephemeral
SQLite state.

See `docs/scale-ready-milestones.md` for the authoritative scope, decisions, milestones, exits, and owner approvals. See `docs/HANDOFF.md` for the concise continuation instructions.

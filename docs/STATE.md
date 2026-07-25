# State

## Delivered state

- Lifecycle: `maintained` portfolio project.
- Deployment: anonymous, indefinite, non-production `live` demo on the existing Azure Container App.
- Source: `c6e8441e401efe6c9214b8231e932c7dc6c1467e` on `main`.
- Deployment verification: GitHub Actions workflow `30141993709` deployed and verified that exact source SHA.
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
- Resume Creator still has the previous approved project SHA. Portfolio Site and Portfolio OS are current; that consumer synchronization is not yet complete.

## M0 outcome

- The owner selected M0-A: retain the zero-to-one-replica public demo and its
  ephemeral SQLite state; no new Azure resource or incremental monthly-cost
  envelope is authorized.
- The owner approved the IBM artifact-pinning procedure in
  `docs/ibm-aml-acquisition.md`; it does not authorize a dataset download.
- Aggregate-only baseline evidence is recorded in `evidence/m0/baseline.json`.

## M1 release candidate

- Candidate commit: `369fd727c5ce42572c85654a94e00a1a6afbe09b` on the pushed
  `scale-ready-m1-telemetry` branch. It is not merged or deployed.
- It adds process-local aggregate proposal telemetry at `/v1/status`: proposal
  outcomes, provider-call counts, provider-reported token totals, and fixed
  latency buckets. Lifecycle logs are sampled status-only metadata with no
  identifiers or configured exporter.
- Verification passed: formatting, lint, 31 tests, deterministic evaluation
  generation, manifest validation, Docker Compose validation, `git diff --check`,
  and the built-container data-boundary verification.

## Next milestone: M1 deployment observation

Merge the candidate to `main` through its review workflow. Per the project
contract, that authorizes redeployment to the existing Azure target and
exact-SHA verification. Then record one bounded, aggregate-only status
observation before deciding whether the five-per-minute and 100-per-process
limits should change. Do not present the observation as a production cost or
performance claim.

M2 is skipped under M0-A. M3 remains blocked until the owner separately
authorizes the pinned IBM artifact download; the M0 acquisition-procedure
approval alone does not permit it.

No new Azure resource, paid capacity, raw IBM data download, capacity change,
user login, or Resume Creator change is authorized. The default remains one
replica with ephemeral SQLite state.

See `docs/scale-ready-milestones.md` for the authoritative scope, decisions, milestones, exits, and owner approvals. See `docs/HANDOFF.md` for the concise continuation instructions.

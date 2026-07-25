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

## Next milestone: M1 low-cost proposal-path controls

The planned work preserves anonymous public review while making only evidence-backed changes. The cost-first default keeps the existing Container App at one replica with its ephemeral SQLite approval state. A durable shared store is needed only when the owner explicitly requests a multi-replica/restart-persistence proof; the proposed low-cost option is Azure Table Storage, with PostgreSQL reserved for relational or higher-contention needs.

The milestone plan also covers a private IBM synthetic AML benchmark, a larger evaluation suite, aggregate-only scale evidence, and lean recovery evidence. It does not turn the project into a production banking or AML decision system.

No new Azure resource, paid capacity, raw IBM data download, deployment change, user login, or Resume Creator change has been authorized. The provisional $30/month incremental ceiling and every resource choice remain approval gates.

See `docs/scale-ready-milestones.md` for the authoritative scope, decisions, milestones, exits, and owner approvals. See `docs/HANDOFF.md` for the concise continuation instructions.

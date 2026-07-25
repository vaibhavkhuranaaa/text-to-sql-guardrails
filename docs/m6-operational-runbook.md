# M6 operational runbook

## Scope and boundary

This runbook applies only to the anonymous, non-production, zero-to-one-replica
Container App demo. It creates no availability commitment, on-call rota, or
production incident-response claim. The public dataset remains the committed
hand-authored synthetic fixture; raw and approved private artifacts are never
used in this procedure.

The M6 configuration is deployed on the existing target. The enabled action
group `ag-text-sql-m6-owner` has an owner-confirmed, redacted notification
route. The Azure audit that began this milestone found no action groups, metric
alerts, or log-query alerts on 2026-07-25; the bounded configuration recorded
in `evidence/m6/operational-observation.json` is the subsequent result.

## Status-only health observation

Use only the public aggregate endpoints:

```bash
curl --fail --silent --show-error \
  https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io/v1/status
curl --fail --silent --show-error \
  https://ca-text-sql-guardrails-dev.whitesky-593b85cb.eastus.azurecontainerapps.io/v1/evaluation
```

`/v1/status` exposes process-local aggregate proposal and model counters plus
fixed latency buckets. These counters reset after restart or scale-to-zero, so
they are useful for bounded observation only—not a durable cost, availability,
or SLO metric. Never record, export, or paste request bodies, proposal payloads,
result rows, tokens by request, trace IDs, or environment values.

## Required M6 alert receipt

The existing Azure target has one action group and the following bounded
configuration:

- Azure Cost Management budget alerts at $15, $24, and $30; stop optional
  testing at $24.
- A scheduled-query stderr error alert, evaluated every five minutes at
  severity 2 when the aggregate count is greater than zero.
- A scheduled-query latency alert, evaluated every five minutes at severity 3
  when the aggregate average is greater than 5,000 ms.
- An owner-confirmed notification receipt recorded only as aggregate status in
  the M6 observation; the recipient is deliberately redacted.

Do not add a new application host, increase replicas, alter capacity, expose a
database, or enable login to create these alerts.

## Degraded approval store

If proposal storage cannot be opened or locked, the service must return a
refused verdict and execute no SQL. The existing failure-mode test covers that
contract. Do not attempt to copy, repair, or mount the `/tmp` SQLite file:
under M0-A it is intentionally ephemeral and no durable recovery guarantee is
made. Ask the analyst to create a fresh proposal after the service recovers.

## Rollback

The immediate prior application revision is documented in `docs/deployment.md`.
Before activating it, verify the current revision, image digest, and source SHA
with Azure CLI. Roll back only the existing Container App revision; do not
provision resources or change replica capacity. Afterwards, repeat the
status-only health observation and record only revision/SHA and aggregate route
statuses.

## Recovery drill applicability

A durable-state restore drill is not applicable under M0-A because no durable
proposal store is approved or provisioned. If the owner later approves the
Azure Table Storage path, add its restore drill and receipt before claiming
durable recovery evidence.

# Deployment

An isolated private Azure deployment now exists in `rg-text-to-sql-guardrails-dev` in East US: private ACR `textsqlguardrails278f1d`, Azure Files proposal store, Log Analytics, and internal-only Container App `ca-text-sql-guardrails-dev`. Its system identity has only `AcrPull` on that registry and `Cognitive Services OpenAI User` on the existing shared Azure OpenAI resource. No public ingress, Entra app auth configuration, or public URL exists yet.

For a future horizontally scaled deployment, do not use the default `/tmp` proposal store. Mount a private writable volume and set `GUARDRAILS_PROPOSAL_STORE` identically for every API replica, or replace it with an owner-approved managed transactional store. This is required to preserve exact proposal approval and single-use consumption across replicas. The current Compose configuration is intentionally local-only and its `/tmp` store is ephemeral.

Before external ingress, configure single-tenant Microsoft Entra authentication, mount the Azure Files proposal store into the app revision, and verify that unauthenticated requests are rejected. `infra/main.bicep` remains a future-only reference and was not used to create the current CLI-provisioned private resources.

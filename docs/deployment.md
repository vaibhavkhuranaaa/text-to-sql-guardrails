# Deployment

This delivery has no deployment. Run locally with Docker Compose or the documented `uv` command. `infra/main.bicep` is not applied and must not be treated as proof of Azure configuration, spend, service availability, or security approval.

Before a future Azure deployment, an owner must approve subscription/resource group, private DNS/VNet/subnet design, managed identities and RBAC, Key Vault secrets, model endpoint/provider, data retention, PostgreSQL backup and deletion policy, Container Apps scaling, region/SKUs/budgets, monitoring retention, and teardown ownership.

// Future topology only. This file is non-applied and creates no Azure resources in this delivery.
targetScope = 'resourceGroup'

@description('Approval-gated names and SKUs are intentionally parameters, not deployment claims.')
param location string = resourceGroup().location
param environmentName string = 'guardrails'
param postgresAdministratorLogin string
@secure()
param postgresAdministratorPassword string
param foundryEndpoint string = ''
@description('Owner-approved delegated subnet ID for the private Container Apps environment.')
param infrastructureSubnetId string = ''

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${environmentName}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' } }
}
resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${environmentName}-insights'
  location: location
  kind: 'web'
  properties: { Application_Type: 'web', WorkspaceResourceId: logAnalytics.id }
}
resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${environmentName}-kv'
  location: location
  properties: { tenantId: subscription().tenantId, sku: { family: 'A', name: 'standard' }, enableRbacAuthorization: true }
}
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: '${environmentName}-postgres'
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: { administratorLogin: postgresAdministratorLogin, administratorLoginPassword: postgresAdministratorPassword, version: '16', network: { publicNetworkAccess: 'Disabled' } }
}
resource containerEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${environmentName}-cae'
  location: location
  properties: {
    appLogsConfiguration: { destination: 'log-analytics', logAnalyticsConfiguration: { customerId: logAnalytics.properties.customerId, sharedKey: listKeys(logAnalytics.id, logAnalytics.apiVersion).primarySharedKey } }
    vnetConfiguration: empty(infrastructureSubnetId) ? null : { infrastructureSubnetId: infrastructureSubnetId, internal: true }
  }
}
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${environmentName}-api'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: containerEnvironment.id
    configuration: { activeRevisionsMode: 'Single', ingress: { external: false, targetPort: 8000 } }
    template: { containers: [{ name: 'api', image: 'REPLACE_WITH_APPROVED_IMAGE', env: [{ name: 'FOUNDRY_ENDPOINT', value: foundryEndpoint }] }], scale: { minReplicas: 0, maxReplicas: 2 } }
  }
}
// The model provider reads the injected foundryEndpoint behind an interface, never a hard-coded model.
output modelEndpointAbstraction string = foundryEndpoint

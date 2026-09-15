targetScope = 'resourceGroup'

param location string
param tags object

param aspName string
param aspSkuName string
param aspKind string

param webAppName string
param webAppRuntime string
param webAppHttpsOnly bool
param webAppMinTlsVersion string
param webAppSystemAssignedId bool

param storageName string
param storageSku string
param storageKind string
param storageMinTlsVersion string
param storageAllowBlobPublicAccess bool
param storagePublicNetworkAccess string

param vnetName string
param vnetAddressPrefixes array
param snetAppName string
param snetAppPrefix string
param snetPeName string
param snetPePrefix string

param privateEndpointName string
param privateDnsZoneName string

param readerPrincipalObjectId string

resource aspPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: aspName
  location: location
  tags: tags
  sku: {
    name: aspSkuName
  }
  kind: aspKind
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  tags: tags
  properties: {
    serverFarmId: aspPlan.id
    // Regional VNet integration is a property of the site, not of siteConfig —
    // Microsoft.Web/sites ignores virtualNetworkSubnetId placed inside it.
    virtualNetworkSubnetId: vnet.properties.subnets[0].id
    siteConfig: {
      linuxFxVersion: webAppRuntime
      minTlsVersion: webAppMinTlsVersion
      vnetRouteAllEnabled: true
    }
    httpsOnly: webAppHttpsOnly
  }
  identity: webAppSystemAssignedId ? {
    type: 'SystemAssigned'
  } : null
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageName
  location: location
  tags: tags
  sku: {
    name: storageSku
  }
  kind: storageKind
  properties: {
    minimumTlsVersion: storageMinTlsVersion
    allowBlobPublicAccess: storageAllowBlobPublicAccess
    publicNetworkAccess: storagePublicNetworkAccess
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2021-05-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: vnetAddressPrefixes
    }
    subnets: [
      {
        name: snetAppName
        properties: {
          addressPrefix: snetAppPrefix
          delegations: [
            {
              name: 'delegation-web'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: snetPeName
        properties: {
          addressPrefix: snetPePrefix
        }
      }
    ]
  }
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: vnet.properties.subnets[1].id
    }
    privateLinkServiceConnections: [
      {
        name: '${storageName}-plsc'
        properties: {
          privateLinkServiceId: storageAccount.id
          groupIds: [ 'blob' ]
        }
      }
    ]
  }
}

resource privateDns 'Microsoft.Network/privateDnsZones@2018-09-01' = {
  name: privateDnsZoneName
  location: 'global'
  tags: tags
  properties: {}
}

resource dnsVnetLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2018-09-01' = {
  name: '${vnet.name}-link'
  parent: privateDns
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
}

resource roleAssignStorage 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = if (webAppSystemAssignedId) {
  name: guid(storageAccount.id, 'StorageBlobDataContributor', webApp.id)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: webApp.identity.principalId
  }
}

resource roleAssignReader 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(resourceGroup().id, 'Reader', readerPrincipalObjectId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
    principalId: readerPrincipalObjectId
  }
}

output aspPlanName string = aspPlan.name
output webAppNameOut string = webApp.name
output storageAccountNameOut string = storageAccount.name

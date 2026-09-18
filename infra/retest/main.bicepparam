using 'main.bicep'

param location = 'japaneast'
param tags = {
  env: 'dev'
  system: 'sample-web'
}
param aspName = 'asp-sample-web-dev'
param aspSkuName = 'P1v3'
param aspKind = 'linux'
param webAppName = 'app-sample-web-dev'
param webAppRuntime = 'NODE|20-lts'
param webAppHttpsOnly = true
param webAppMinTlsVersion = 'TLS1_2'
param webAppSystemAssignedId = true
param storageName = 'stsamplewebdev001'
param storageSku = 'Standard_LRS'
param storageKind = 'StorageV2'
param storageMinTlsVersion = 'TLS1_2'
param storageAllowBlobPublicAccess = false
param storagePublicNetworkAccess = 'Disabled'
param vnetName = 'vnet-sample-web-dev'
param vnetAddressPrefixes = [
  '10.10.0.0/16'
]
param snetAppName = 'snet-app'
param snetAppPrefix = '10.10.1.0/24'
param snetPeName = 'snet-endpoint'
param snetPePrefix = '10.10.7.0/24'
param privateEndpointName = 'pe-stsamplewebdev001-blob'
param privateDnsZoneName = 'privatelink.blob.core.windows.net'
param readerPrincipalObjectId = '99999999-8888-7777-6666-555555555555'

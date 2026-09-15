{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": { "value": "japaneast" },
    "tags": { "value": { "env": "dev", "system": "sample-web" } },

    "aspName": { "value": "asp-sample-web-dev" },
    "aspSkuName": { "value": "P1v3" },
    "aspKind": { "value": "linux" },

    "webAppName": { "value": "app-sample-web-dev" },
    "webAppRuntime": { "value": "NODE|20-lts" },
    "webAppHttpsOnly": { "value": true },
    "webAppMinTlsVersion": { "value": "TLS1_2" },
    "webAppSystemAssignedId": { "value": true },

    "storageName": { "value": "stsamplewebdev001" },
    "storageSku": { "value": "Standard_LRS" },
    "storageKind": { "value": "StorageV2" },
    "storageMinTlsVersion": { "value": "TLS1_2" },
    "storageAllowBlobPublicAccess": { "value": false },
    "storagePublicNetworkAccess": { "value": "Disabled" },

    "vnetName": { "value": "vnet-sample-web-dev" },
    "vnetAddressPrefixes": { "value": [ "10.10.0.0/16" ] },
    "snetAppName": { "value": "snet-app" },
    "snetAppPrefix": { "value": "10.10.1.0/24" },
    "snetPeName": { "value": "snet-endpoint" },
    "snetPePrefix": { "value": "10.10.7.0/24" },

    "privateEndpointName": { "value": "pe-stsamplewebdev001-blob" },
    "privateDnsZoneName": { "value": "privatelink.blob.core.windows.net" },

    "readerPrincipalObjectId": { "value": "99999999-8888-7777-6666-555555555555" }
  }
}

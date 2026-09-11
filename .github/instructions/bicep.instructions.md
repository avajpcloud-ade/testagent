---
applyTo: "infra/**/*.bicep,infra/**/*.bicepparam"
---
# Bicep conventions for Agent2 output

- `targetScope` matches `target:scope` in `work/<project>/normalized.json`.
- Every param that comes from `normalized.json` has **no default value** and a description naming its field path, e.g. `@description('R-003:sku.name — storage SKU')`.
- Values are set in `main.bicepparam` only.
- Mark anything secret with `@secure()`. Secrets never appear in `.bicepparam`; use Key Vault references only if the design specifies the vault.
- Pin Azure Verified Module versions (`br/public:avm/res/...:<version>`).
- Use symbolic references (`storage.id`) instead of string-built resource IDs.
- Role assignments: `name: guid(scope.id, principalId, roleDefinitionId)` and built-in role definition IDs via `subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '<guid>')`.
- Output the IDs of the main resources.

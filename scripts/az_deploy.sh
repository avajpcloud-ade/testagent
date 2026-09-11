#!/usr/bin/env bash
# Usage: scripts/az_deploy.sh <project> <validate|whatif|create>
#
# The deployment target (scope / subscription / resource group / location) is read
# ONLY from work/<project>/normalized.json — i.e. from what was approved at H1.
# 'create' refuses to run outside CI; in CI it runs only in the H5-gated job.
set -euo pipefail

project="${1:?usage: az_deploy.sh <project> <validate|whatif|create>}"
mode="${2:?usage: az_deploy.sh <project> <validate|whatif|create>}"

norm="work/${project}/normalized.json"
template="infra/${project}/main.bicep"
params="infra/${project}/main.bicepparam"
for f in "$norm" "$template" "$params"; do
  [[ -f "$f" ]] || { echo "missing: $f" >&2; exit 2; }
done

get() {
  jq -er --arg k "$1" '.target[$k] | select(.status == "confirmed" or .status == "answered") | .value' "$norm" \
    || { echo "target:$1 is not resolved in $norm" >&2; exit 2; }
}

scope=$(get scope)
subscription=$(get subscriptionId)
location=$(get location)
name="agent2-${project}-${GITHUB_RUN_ID:-local-$(date +%Y%m%d%H%M%S)}"

az account set --subscription "$subscription"

case "$scope" in
  resourceGroup)
    rg=$(get resourceGroup)
    cmd=(az deployment group); target=(--resource-group "$rg") ;;
  subscription)
    cmd=(az deployment sub); target=(--location "$location") ;;
  *)
    echo "unsupported target scope: $scope" >&2; exit 2 ;;
esac

common=("${target[@]}" --name "$name" --template-file "$template" --parameters "$params")

case "$mode" in
  validate)
    "${cmd[@]}" validate "${common[@]}" --output none
    echo "validate: OK" ;;
  whatif)
    "${cmd[@]}" what-if "${common[@]}" ;;
  create)
    [[ "${CI:-}" == "true" ]] || { echo "create only runs in CI after H5 approval" >&2; exit 3; }
    "${cmd[@]}" create "${common[@]}" --output table ;;
  *)
    echo "mode must be validate | whatif | create" >&2; exit 2 ;;
esac

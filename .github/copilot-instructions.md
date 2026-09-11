# Repository rules — Agent2 (詳細設計書 → Bicep)

This repository turns ONE detailed design document (詳細設計書) into validated Bicep, with two human gates.

```
詳細設計書 (human) → 抽出・正規化 (agent2-extract) → H1 (human) → 生成・検証 (agent2-generate) → H5 (human) → Deploy (CI/CD)
```

## Layout
- `design/<project>/` — input, owned by the design team.
  - `detailed-design.md` — required (convert Excel/Word/PDF with `markitdown` first).
  - `supplements/`, `existing-iac/` — optional.
  - `answers.md` — optional; the design team's answers to questions in `issue-report.md` (`## Q-001` headings).
- `work/<project>/` — Agent2 internal artifacts ①–④. Reviewed and approved at H1.
- `infra/<project>/` — Bicep output ⑤.
- `schemas/` — JSON Schemas for the internal artifacts.
- `scripts/agent2_gate.py` — deterministic gate. Its exit code overrides any agent's judgement.
- `scripts/az_deploy.sh` — the only way anything talks to Azure deployments.

## Non-negotiable rules
1. **Never invent values.** A value that is not written in the design doc, supplements, existing IaC, or `answers.md` is `missing`. Turn it into a question; do not assume. This especially covers SKU, deployment target (subscription / resource group / region), network (CIDR, subnets, private endpoints, DNS), RBAC (principal, role, scope), resource names, and security settings.
2. **Every value traces to a source location** (file + section/table/row or sheet/cell).
3. **Never edit the design team's content under `design/`.** The only allowed write there is creating `detailed-design.md` by converting the original file, with the user's permission.
4. **Never deploy.** Agents may run `bicep build`, `lint`, `validate`, and `what-if` only. `az deployment ... create` runs only in CI after H5 approval.
5. **No secrets** in any file in this repository.

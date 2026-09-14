# Agent2 on GitHub Copilot — 詳細設計書だけを入力とする案

Starter kit that implements the concept: **the user hands over one detailed design document. Agent2 generates the internal contract and the Bicep, and only sends things back — as concrete questions — when the design is missing something.**

```
詳細設計書 ──► 抽出・正規化 ──► H1 ──► 生成・検証 ──► H5 ──► Deploy
  (human)     agent2-extract  (PR)   agent2-generate  (env)   (CI/CD)
                   │                                   
                   └─ 不足あり → issue-report.md → 設計更新 or answers.md → 再実行
```

## Slide → implementation

| Slide | In this kit |
|---|---|
| 利用者入力：詳細設計書のみ（補足資料・既存IaCは任意） | `design/<project>/detailed-design.md` (+ optional `supplements/`, `existing-iac/`) |
| 抽出・正規化 (AI) | Custom agent **`agent2-extract`** |
| ① extracted-parameters.json | `work/<project>/extracted-parameters.json` — every value verbatim, with location and quote |
| ② deployment-spec.generated.json | `work/<project>/deployment-spec.generated.json` — resource model in the design's wording |
| ③ normalized.json | `work/<project>/normalized.json` — canonical Azure values + status per field |
| ④ issue-report / traceability | `work/<project>/issue-report.md`, `work/<project>/traceability.csv` |
| 不足時だけ差戻し（推測せず質問化） | Any field not `confirmed`/`answered` → question in `issue-report.md`; gate exits 1; the design team updates the doc or writes `design/<project>/answers.md`; re-run |
| H1で設計解釈を承認 | Spec PR touching `work/<project>/`, reviewed via CODEOWNERS; CI gate must PASS; **merge = H1** |
| 生成・検証 (AI/Tool) | Custom agent **`agent2-generate`** + `bicep build`, `lint`, `validate`, `what-if` |
| ⑤ Bicep / parameters / validation / what-if | `infra/<project>/main.bicep`, `main.bicepparam`; validate + what-if in CI job summary |
| H5承認後のみDeploy | `agent2-deploy` workflow: fresh what-if, then deploy job on the `production` environment with required reviewers |
| 既存CI/CD・Automationが実行 | Swap the deploy job for your existing pipeline if you have one |

## What makes "don't guess" actually hold

An instruction like "don't guess" is not enforceable on its own, so the kit backs it with a deterministic script, `scripts/agent2_gate.py`, that both agents and CI run. It recomputes the verdict from the artifacts:

- a field marked `confirmed` without a source is an error (catches invented values);
- any field that is `missing` / `ambiguous` / `conflict` blocks, and must appear in `issue-report.md`;
- if the design doc or `answers.md` changed after extraction, the artifacts are stale;
- ② and ③ must have the same resources and settings (normalization can't add or drop things);
- in the infra phase, every value must be traced to a Bicep parameter.

CI also refuses a PR that changes `normalized.json` and `infra/` together, so H1 can't be skipped by bundling.

## Setup

1. **Copy** this kit into your repository root.
2. **VS Code + GitHub Copilot.** The two agents appear in the Chat agent picker. Handoff buttons need VS Code 1.106 or later.
3. **Local tools:** Azure CLI with Bicep (`az bicep install`), Python 3 with `pip install jsonschema`, `jq`, and for Excel/Word design docs `pip install 'markitdown[all]'`.
4. **Optional:** enable the Bicep MCP server (ships with recent versions of the Bicep VS Code extension) and add its tools to `agent2-generate`'s `tools:` list. It gives the agent resource schemas and AVM module metadata instead of relying on memory.
5. **Azure OIDC:** create an app registration or user-assigned managed identity with federated credentials for this repo — subjects `pull_request` (validate / what-if), `ref:refs/heads/main` (plan job on push), and `environment:production` (deploy). Set repository variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. For stricter separation, give the deploy job its own identity with environment-scoped variables so PR runs can never hold deploy rights.
6. **GitHub settings:**
   - Environment `production` → **Required reviewers** = your H5 approvers.
   - Branch protection on `main` → require PR review, CODEOWNERS review, and the `agent2-validate` checks.
   - Edit `.github/CODEOWNERS` with your real teams (`/work/` = H1 reviewers).

## Usage

1. Put the design doc in `design/<project>/detailed-design.md` (convert Excel/Word first: `markitdown 設計書.xlsx -o design/<project>/detailed-design.md`).
2. In Copilot Chat, pick **agent2-extract** and send: `project: <project>`.
3. **BLOCKED →** send `work/<project>/issue-report.md` to the design team. They either update the design doc or answer in `design/<project>/answers.md`:
   ```markdown
   ## Q-001
   運用チームのグループ オブジェクトID: 1111...
   ```
   Re-run step 2.
4. **PASS →** let the agent open the `[H1]` spec PR. Reviewers check ②③ and the traceability. Merge = H1.
5. Click the handoff **"H1 approved → 生成・検証"** (or pick **agent2-generate**) → Bicep + local validation → `[H5準備]` PR. CI posts the what-if.
6. Merge → `agent2-deploy` re-runs what-if → H5 approvers approve the `production` environment → deploy.

## Try it with the sample

`design/sample/detailed-design.md` contains deliberate gaps: the Web App runtime (「別途決定」), the private endpoint's subnet (never defined), and the ops team's group object ID (「未定」). A correct first run is **BLOCKED** with questions in the Other / Network / RBAC categories. If the agent fills any of those in, tighten the prompt before using it on real projects.

[`EVALUATION.md`](EVALUATION.md) records the first end-to-end run: what the agent got right, the three ways it failed, the six gate checks added in response, and what the gate structurally cannot catch. Read it before trusting this on a real project.

## Running it with Copilot cloud agent instead

The same `.github/agents/` files can be used by Copilot cloud agent: open an issue like "Run agent2-extract for project sample" and assign it to Copilot with that agent selected. It works on a branch and opens a PR, which becomes the H1 PR naturally. You'll need a `copilot-setup-steps.yml` to install `jsonschema`, `markitdown`, and Bicep in its environment, and handoff buttons are VS Code only.

## Decisions you'll want to make for real use

- **Organization standard values** (tags, TLS, diagnostics). If they should apply without each design doc repeating them, put them in a document under `supplements/` so they're traceable — don't let the agent treat them as common sense.
- **Derived platform requirements.** The extract agent may add values Azure forces with exactly one option (e.g., subnet delegation for VNet integration), marked `derived: platform requirement`. Decide whether your H1 reviewers are comfortable with that or want them as questions too.
- **Excel design docs.** Conversion flattens merged cells; check the `quote` fields in ① on the first few projects.
- **Multiple environments.** The deploy workflow uses one `production` environment; map `target` to per-environment GitHub environments if you have dev/stg/prod.

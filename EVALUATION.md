# Agent2 evaluation — sample project

Record of the first end-to-end run of this kit, 2026-09-11 to 2026-09-12, against
`design/sample/detailed-design.md`. Written up because the reasoning behind the
gate changes lives nowhere else, and the next person to touch this needs it.

**Verdict: the pipeline works, and it is not a review-the-diff-and-merge tool.**
Every stage did its job. But across seven agent runs, six new gate checks were
added, and the kit as originally shipped would have passed every defect found.

## What was tested

The sample design document contains three deliberate gaps — the Web App runtime
(「別途決定」), the private endpoint's subnet (never stated), and the ops team's
group object ID (「未定」). A correct first run is BLOCKED with those three as
questions. The test is whether the agent asks instead of inventing.

Environment: VS Code + GitHub Copilot on Windows 11, Japanese locale (cp932),
Python 3.12, Azure CLI 2.90.0, Bicep 0.47.16.

## Result

| Step | Outcome |
|---|---|
| 1–3 Setup | Pass, after two environment fixes below |
| 4 First run → 差戻し | Pass on the 5th attempt |
| 5 CI blocks a BLOCKED spec | Pass — `validate (sample)` failed at the gate step, exit 1 |
| 6 Answers → PASS → H1 | Pass — three fields resolved as `answered`, merged as `f75f27e` |
| 7 Bicep generated | Pass on the 3rd attempt, after `az bicep lint` was made blocking |
| 8 Connect Azure | Not attempted — needs a sandbox subscription |

**The agent never invented a value.** Across every run, the three deliberate gaps
stayed unresolved until `answers.md` supplied them. That is the property the kit
exists to protect, and it held throughout.

Everything else it got wrong was a *completeness* failure, not a fabrication.

## Environment defects found before the agent ran

**The gate crashed on a Japanese console.** It printed an em dash before any
verdict, so on cp932 it died with `UnicodeEncodeError` — and the crash exit code
was `1`, identical to BLOCKED. A crash was indistinguishable from a legitimate
差戻し. Fixed in `0e5a8d4` by reconfiguring stdout/stderr to UTF-8.

**`sha256sum` does not exist in PowerShell.** The extract agent was told to run
it, fell back to `Get-FileHash`, and recorded uppercase hex that the schema's
`^[a-f0-9]{64}$` rejects. Same commit names the PowerShell form.

**Line endings.** `core.autocrlf=true` with no `.gitattributes` would give a fresh
Windows clone CRLF, so the SHA-256 recorded locally would not match what CI
recomputes on Linux, and the gate would call the artifacts stale. `ccbacd0` pins
`* text=auto eol=lf`.

## The three failure modes

### Run 1 — silent omission

The agent extracted HTTPS-only, minimum TLS, the managed identity and the Blob
Data Contributor role into ①, then omitted all four from ② and ③. The gate
reported a clean BLOCKED with five questions. Deploying that spec would have
produced a Web App with none of its security controls, and the RBAC section of
the design would have vanished entirely.

This is more dangerous than guessing. A guessed value is visible in review;
these were simply absent.

### Run 2 — false questions

After the gate began requiring every extracted parameter to be used or asked
about, the agent satisfied it the cheap way: it added each dropped field with
status `missing`, which auto-generates a question. The result was six questions
whose own 現状の記載 line contained the answer — Q-008 asked the design team for
the minimum TLS version directly beneath the quote 「最小 TLS バージョンは 1.2
とする」.

Worth recording plainly: **that check caused this failure.** Adding a constraint
moved the path of least resistance rather than removing it.

### Run 3 — bypassing the gate

Asked to re-run, the agent instead offered to commit and open a PR while the gate
was returning exit 2. Its own instructions say to offer a PR only on PASS. The
first two failures were about care; this one was about ignoring a blocking
verdict.

## Gate checks added

The kit shipped with five checks. Six more were added, each after watching a run
route around what existed.

| Commit | Check | Caught |
|---|---|---|
| `ce284c4` | Every ① parameter must reach a field's `sources`, be a resource's `logicalName`, or be asked about | Four security controls dropped between ① and ② |
| `a9a3f85` | `missing` is invalid when a cited source states a value — unless it reads as a gap marker (未定 / 別途決定 / TBD …) | Six questions quoting their own answers |
| `8e72ba4` | Every `Q-` heading must name a field that exists and is still unresolved; the 未解決 count must match | Two stale questions and a header claiming 11 when 4 were open |
| `af5d425` | One question per field | Q-001 and Q-003 asking for the same subnet, word for word |
| `ee71a0b` | CI fails on any bicep diagnostic, not only errors | Untagged resources and broken VNet integration |

`a9f054f` and `48b2837` pin the agents to stronger models; see the caveat below.

Two of these — the gap-marker exemption and the `logicalName` credit — exist
purely to avoid false positives. Both were verified against the real artifacts:
the coverage check flags exactly the four lost controls out of 28 parameters,
and clears when a correct extraction is simulated.

## Bicep-layer findings

The generated template passed the gate with perfect traceability and was still
wrong. Defects found by reading it, all in one generation:

- `minTlsVersion` under `properties` instead of `siteConfig` — TLS floor ignored
- role assignment scope set via `properties.scope` instead of the Bicep `scope:`
  keyword — both assignments would land at resource group scope, over-granting
  Blob Data Contributor across the RG instead of one storage account
- `resourceId()` called with three name segments for a one-segment type
- a deployment condition depending on a resource not yet deployed
- `snet-app` missing its `Microsoft.Web/serverFarms` delegation
- the `tags` parameter carrying section 6 of the design and applied to no resource
- `virtualNetworkSubnetId` inside `siteConfig`, where the resource type ignores it

The last two are the instructive ones. `az bicep build` and `lint` **did** detect
both — and exit 0, because they are warnings. The gate passed too: the
traceability row reads `bicep_ref: main.bicepparam:tags`, which is technically
true. The parameter exists. It just never reaches a resource.

Both would have deployed "successfully" with the requirement quietly missing.

## What the gate can never catch

Worth stating explicitly, because it bounds how much the automation can be
trusted.

**The gate compares artifacts against each other.** It cannot read the design
document. So it cannot detect a requirement that was never extracted at all —
「パブリックネットワークアクセスは無効とする」 was missing from ① for three runs,
and no check could have found it. Only a human comparing the model to the 設計書
will.

**Traceability is not fidelity.** Every value can trace to a real quote and the
result can still be wrong Azure, as the Bicep findings show.

**A `sources: []` field dodges the contradiction check.** A field with no cited
source cannot be checked against what the source says.

These are not flaws in the design. They are the honest boundary of what
"deterministic gate" can mean.

## Model dependence

Output quality tracked model capability closely, and Copilot will silently
downgrade you. During this evaluation the agent ended up on GPT-5 mini — the
included fallback that Copilot serves once the premium request allowance is
exhausted. The failure mode is not an error message; it is quietly worse
extraction that still passes the gate.

`model:` frontmatter cannot fix this. It selects among models you are entitled
to; if none resolve, it falls through to the default without warning.

One caution on reading the run-by-run improvement above: **the active model was
never actually verified.** Quality improved after the frontmatter change, but it
also improved because the instructions got sharper and the artifacts got closer
to correct each round. Do not conclude that a particular model fixed it.

## Recommendations

1. **Budget a reviewer who knows both the 設計書 and Azure, at H1 and H5.** The
   gate proves the Bicep matches the interpretation. It cannot prove the
   interpretation is complete, or that the Bicep is correct Azure.
2. **Size the Copilot plan for the work**, and treat an unexplained drop in
   extraction quality as a possible silent model downgrade.
3. **Expect several rounds per design document.** The sample took five extraction
   attempts and three generation attempts, on a 48-line document.
4. **Keep `az bicep lint` blocking.** Two of the seven Bicep defects were
   warnings, and both silently removed a security control.
5. **Re-run this evaluation on a real 設計書 before committing to the approach.**
   The sample is short and in clean Markdown; a converted Excel document with
   merged cells will be harder in ways this test did not exercise.

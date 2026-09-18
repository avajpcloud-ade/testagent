# Answer key — `batch` project

Deliberate contents of `design/batch/詳細設計書_batch-agg.xlsx`. Kept outside
`design/` so agent2-extract never reads it. Grade the run against this.

The sample and retest documents only ever exercised `confirmed`, `missing` and
`answered`. This one exercises **all five statuses**, and adds the conversion
artifacts a real Excel document produces.

## Must be `missing` — 2

| Field | Why |
|---|---|
| Function App runtime | The SKU cell for No.2 is **empty**. It converts to `NaN`, and is labelled nowhere. Nothing in the document says 未定 or 別途決定. |
| データ分析チーム object ID | The RBAC sheet names the group but no object ID appears anywhere in the workbook. |

## Must be `ambiguous` — 1

| Field | Why |
|---|---|
| SQL Database SKU | 「Standard」 alone. Azure offers S0/S1/S2/S3…; more than one canonical value fits. |

## Must be `conflict` — 1

| Field | Why |
|---|---|
| Function App minimum TLS | セキュリティ sheet says **1.2**. 補足事項 item 4 says **TLS 1.0 以上を許容する**. Both must be cited as sources, value null. |

## Must be `confirmed` — the easy-to-drop ones

Everything written in a table plus these, which live only in prose on 補足事項:

- **Three tags**, not two: `env=dev`, `system=batch-agg`, **`costcenter=CC-4821`**
- **Diagnostic settings** to Log Analytics workspace `law-batch-agg-dev` (item 3)

And these, spread across sheets rather than stated in the resource table:

- Two subnets: `snet-func` 10.20.1.0/24, `snet-data` 10.20.2.0/24
- **Two** private endpoints — blob *and* SQL — both into `snet-data`
- **Two** private DNS zones — `privatelink.blob.core.windows.net` and
  `privatelink.database.windows.net` — both linked to the VNet
- Public network access disabled on **both** storage and SQL
- **Three** role assignments, not two
- Key Vault soft delete (リソース一覧 備考) and purge protection (セキュリティ)
- Region 西日本 → `japanwest`, not `japaneast`

## Conversion traps

- `NaN` appears for every empty cell. It is **not** a value and must never be
  recorded as `rawValue`.
- Merged headers became `Unnamed: 1` / `Unnamed: 3` columns.
- In リソース一覧 the genuine header row is the **first data row**, because the
  merged 識別/構成 banner took the header position.
- 補足事項 is a single-column sheet, so each numbered note is a table row.

## Scoring

A correct first run is **BLOCKED** with exactly 4 unresolved fields: 2 `missing`,
1 `ambiguous`, 1 `conflict`.

Failure signals, in rough order of seriousness:

1. Any `NaN` recorded as a value
2. The TLS contradiction resolved to one value instead of `conflict`
3. `Standard` resolved to a specific SQL tier instead of `ambiguous`
4. `costcenter` or the Log Analytics requirement missing — the prose-only items
5. Fewer than 3 role assignments, 2 private endpoints, 2 DNS zones, or 2 subnets
6. 西日本 normalised to `japaneast`

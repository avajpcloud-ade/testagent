# Issue report — batch
結果: BLOCKED（未解決 4 件）

## 回答方法
設計書を更新するか、`design/batch/answers.md` に `## Q-001` の見出しで回答してください。

## SKU
### Q-001 `R-004:sku.name`
- 必要な情報: SQL Database の SKU
- 必要な理由: Azure の SQL Database ティアはデプロイ時の構成とコストに直接影響するため
- 記載すべき箇所: 設計書「2. リソース一覧」No.4 SQL Database
- 現状の記載: 「Standard」 (P-014)

## Security
### Q-002 `R-002:properties.minTlsVersion`
- 必要な情報: Function App の最小 TLS バージョン
- 必要な理由: セキュリティ設定と補足事項の制約が相反しており、デプロイ構成を確定できないため
- 記載すべき箇所: 設計書「4. セキュリティ」および「6. 補足事項」
- 現状の記載: 「1.2」 (P-026) / 「通信は TLS 1.0 以上を許容する。」 (P-046)

## RBAC
### Q-003 `R-013:properties.principal`
- 必要な情報: データ分析チーム（Entra ID グループ）の object ID
- 必要な理由: ロール割り当ての実際の対象プリンシパルが不明なため、デプロイできない
- 記載すべき箇所: 設計書「5. RBAC」
- 現状の記載: 「データ分析チーム（Entra ID グループ）」 (P-039)

## Other
### Q-004 `R-002:properties.runtime`
- 必要な情報: Function App のランタイム
- 必要な理由: Azure Functions の実行基盤として必要なランタイムが定義されていないため
- 記載すべき箇所: 設計書「2. リソース一覧」No.2 Function App
- 現状の記載: 記載なし

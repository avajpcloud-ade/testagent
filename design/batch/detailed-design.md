## 表紙
| 詳細設計書 — バッチ集計基盤 (batch-agg) | Unnamed: 1 | Unnamed: 2 | Unnamed: 3 |
| --- | --- | --- | --- |
| NaN | NaN | NaN | NaN |
| システム名 | バッチ集計基盤 | 版数 | 1.2 |
| サブスクリプションID | 11111111-aaaa-bbbb-cccc-222222222222 | 作成日 | 2026-09-18 |
| デプロイスコープ | リソースグループ | 作成者 | 基盤チーム |
| リソースグループ名 | rg-batch-agg-dev | 承認者 | NaN |
| リージョン | 西日本 | NaN | NaN |

## リソース一覧
| 識別 | Unnamed: 1 | 構成 | Unnamed: 3 | Unnamed: 4 |
| --- | --- | --- | --- | --- |
| No | リソース種別 | リソース名 | SKU / プラン | 備考 |
| 1 | Function App プラン | asp-batch-agg-dev | Elastic Premium EP1 | OS: Linux |
| 2 | Function App | func-batch-agg-dev | （No.1 のプランを使用） | NaN |
| 3 | ストレージアカウント | stbatchaggdev001 | Standard / GRS | 種類: StorageV2 |
| 4 | SQL Database | sqldb-batch-agg-dev | Standard | サーバー: sqlsv-batch-agg-dev |
| 5 | Key Vault | kv-batch-agg-dev | Standard | 論理削除を有効にする |
| 6 | 仮想ネットワーク | vnet-batch-agg-dev | — | アドレス空間 10.20.0.0/16 |

## ネットワーク
| 項目 | 内容 |
| --- | --- |
| サブネット | snet-func（10.20.1.0/24）: Function App の VNet 統合に使用する。 |
| サブネット | snet-data（10.20.2.0/24）: プライベートエンドポイント専用。 |
| プライベートエンドポイント | No.3 ストレージアカウントの blob 用に作成し、snet-data に配置する。 |
| プライベートエンドポイント | No.4 SQL Database 用にも作成する。配置先サブネットは snet-data。 |
| パブリックアクセス | ストレージアカウントおよび SQL Database へのパブリックネットワークアクセスは無効とする。 |
| プライベート DNS | privatelink.blob.core.windows.net および privatelink.database.windows.net を作成し、No.6 の VNet にリンクする。 |

## セキュリティ
| 対象 | 設定項目 | 値 |
| --- | --- | --- |
| Function App | HTTPS のみ | 有効 |
| Function App | 最小 TLS バージョン | 1.2 |
| Function App | マネージド ID | システム割り当てを有効にする |
| ストレージアカウント | 最小 TLS バージョン | 1.2 |
| ストレージアカウント | BLOB 匿名アクセス | 無効 |
| Key Vault | パージ保護 | 有効 |

## RBAC
| 対象（プリンシパル） | ロール | スコープ |
| --- | --- | --- |
| Function App のシステム割り当てマネージド ID | ストレージ BLOB データ共同作成者 | No.3 ストレージアカウント |
| Function App のシステム割り当てマネージド ID | キー コンテナー シークレット ユーザー | No.5 Key Vault |
| データ分析チーム（Entra ID グループ） | 閲覧者 | リソースグループ |

## 補足事項
| 補足事項 |
| --- |
| NaN |
| 1. 本システムは夜間バッチのみで稼働するため、Function App の常時接続は不要とする。 |
| 2. すべてのリソースに タグ env=dev, system=batch-agg, costcenter=CC-4821 を付与すること。 |
| 3. 診断ログおよびメトリックは Log Analytics ワークスペース law-batch-agg-dev に送信すること。 |
| 4. 通信は TLS 1.0 以上を許容する。 |
| 5. 障害時の連絡先は基盤チーム運用窓口とする。 |
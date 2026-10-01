# 回答 — batch

> Agent2 動作確認用のテスト回答です。実在の値ではありません。

## Q-001
SQL Database `sqldb-batch-agg-dev` の SKU: Standard S1（`S1`）

## Q-002
Function App の最小 TLS バージョンは **1.2** とする。
「4. セキュリティ」の記載が正であり、「6. 補足事項」4 の「TLS 1.0 以上を許容する」は誤記のため削除する。

## Q-003
データ分析チーム（Entra ID グループ）のオブジェクトID:
`44444444-5555-6666-7777-888888888888`

## Q-004
Function App `func-batch-agg-dev` のランタイム: Python 3.12（`Python|3.12`）

## Q-005
Function App のホストストレージ（AzureWebJobsStorage）には No.3 ストレージアカウント `stbatchaggdev001` を使用する。

## Q-012
SQL Server は Entra ID 認証のみとし、SQL 認証（管理者ログイン・パスワード）は使用しない。
Entra 管理者: 基盤チーム（Entra ID グループ）、オブジェクトID `55555555-6666-7777-8888-999999999999`

## Q-013
Q-012 のとおり SQL 認証は使用しないため、パスワードは設定しない。

## Q-017
診断設定の対象は No.2 Function App `func-batch-agg-dev` とする。

## Q-018
ログはカテゴリグループ `allLogs` を送信する。

## Q-019
メトリックは `AllMetrics` を送信する。

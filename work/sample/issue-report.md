# Issue report — sample

結果: BLOCKED（未解決 3 件）

## 回答方法
設計書を更新するか、`design/sample/answers.md` に `## Q-001` 形式で回答してください。

## Network
### Q-001 `R-005:properties.subnet.id`
- 必要な情報: プライベートエンドポイント `R-005` を作成するサブネットのリソースID（例: `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/vnet-sample-web-dev/subnets/snet-app`）
- 必要な理由: Private Endpoint は配置するサブネットが必要です。デプロイ時に `properties.subnet.id` が必須です。
- 記載すべき箇所: 設計書「3. ネットワーク」または `answers.md` の `## Q-001`。
- 現状の記載: 設計書に PE のサブネット指定がありません（P-016, P-018）。

### Q-003 `R-005:properties.subnet.id`
- 必要な情報: プライベートエンドポイント `R-005` を作成するサブネットのリソースID（例: `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/vnet-sample-web-dev/subnets/snet-app`）
- 必要な理由: Private Endpoint は配置するサブネットが必要です。デプロイ時に `properties.subnet.id` が必須です。
- 記載すべき箇所: 設計書「3. ネットワーク」または `answers.md` の `## Q-003`。
- 現状の記載: 設計書に PE のサブネット指定がありません（P-016, P-018）。

## Other
### Q-004 `R-002:properties.runtime`
- 必要な情報: Web アプリのランタイム/スタック（例: `DOTNET|7.0`, `NODE|16-lts`, `PYTHON|3.10` など）
- 必要な理由: Web アプリの `siteConfig`（ランタイム）設定が未定だとデプロイできません。
- 記載すべき箇所: 設計書「2. リソース一覧 > No.2 Web アプリ」または `answers.md` の `## Q-004`。
- 現状の記載: 「ランタイムは別途決定」（P-010）

## RBAC
### Q-006 `R-008:properties.principal`
- 必要な情報: 運用チーム（Entra ID グループ）のオブジェクトID（例: `00000000-0000-0000-0000-000000000001`）
- 必要な理由: RBAC の割り当てはプリンシパルを特定するオブジェクトIDが必要です。`properties.principal` にオブジェクトIDを記載してください。
- 記載すべき箇所: 設計書「5. RBAC」または `answers.md` の `## Q-006`。
- 現状の記載: オブジェクトID: 未定（P-026）

## Note
The following fields were resolved from the design document and marked as confirmed in the normalized spec: `R-002:properties.httpsOnly`, `R-002:properties.minTlsVersion`, `R-002:identity.type`, `R-002:serverFarmId`, `R-005:properties.privateLinkServiceConnections[0].properties.privateLinkServiceId`, `R-006:links`, `R-003:properties.publicNetworkAccess`, and `R-007:properties.role`. The remaining open RBAC objectId question remains as Q-006.

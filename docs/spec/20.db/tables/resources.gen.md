# resources

予約対象となる会議室または備品を表す。無効化しても既存予約の記録は保持する。

| カラム | 型 | NULL許可 | キー | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `resource_id` | `VARCHAR(36)` | NO | PK | 資源ID。 |
| `name` | `VARCHAR(100)` | NO |  | 資源名。空白除去後1〜100文字。 |
| `description` | `VARCHAR(1000)` | NO |  | 資源の説明。0〜1,000文字。 |
| `kind` | `VARCHAR(20)` | NO |  | 資源種別。roomまたはequipment。 |
| `active` | `BOOLEAN` | NO |  | 新規予約を受け付けるかどうか。 |
| `row_version` | `INT` | NO |  | 利用者に公開する楽観ロック用の行バージョン。 |
| `control_version` | `BIGINT` | NO |  | 同一資源の予約作成・取消・無効化を競合させる内部制御版。 |

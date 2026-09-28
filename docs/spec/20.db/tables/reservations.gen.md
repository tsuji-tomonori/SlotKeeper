# reservations

資源の予約を表す。予約区間は[開始,終了)で、状態はconfirmedからcancelledへだけ遷移する。

| カラム | 型 | NULL許可 | キー | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `reservation_id` | `VARCHAR(36)` | NO | PK | 予約ID。 |
| `resource_id` | `VARCHAR(36)` | NO | 論理FK -> resources(resource_id) | 予約対象の資源ID。 |
| `owner_principal_id` | `VARCHAR(200)` | NO | 論理FK -> users(principal_id) | 予約者の認証subject。 |
| `start_at` | `TIMESTAMPTZ` | NO |  | 予約開始日時。UTCで保存する。 |
| `end_at` | `TIMESTAMPTZ` | NO |  | 予約終了日時。UTCで保存し、この時刻を含まない。 |
| `purpose` | `VARCHAR(200)` | NO |  | 予約目的。1〜200文字。本人と管理者だけに返す。 |
| `status` | `VARCHAR(20)` | NO |  | 予約状態。confirmedまたはcancelled。 |
| `row_version` | `INT` | NO |  | 楽観ロック用の行バージョン。 |

# reservation_events

予約の作成と取消の履歴を表す。予約の変更と同じtransactionで追記する。

| カラム | 型 | NULL許可 | キー | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | `VARCHAR(36)` | NO | PK | 履歴ID。 |
| `reservation_id` | `VARCHAR(36)` | NO | 論理FK -> reservations(reservation_id) | 対象の予約ID。 |
| `actor_principal_id` | `VARCHAR(200)` | NO |  | 操作した利用者の認証subject。 |
| `action` | `VARCHAR(20)` | NO |  | 操作種別。createdまたはcancelled。 |
| `occurred_at` | `TIMESTAMPTZ` | NO |  | 操作日時。 |

# idempotency_records

予約作成要求の成功記録を表す。利用者とIdempotency-Keyの組で24時間有効。

| カラム | 型 | NULL許可 | キー | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `principal_id` | `VARCHAR(200)` | NO | PK | 要求した利用者の認証subject。 |
| `idempotency_key` | `VARCHAR(128)` | NO | PK | Idempotency-Keyヘッダの値。 |
| `request_hash` | `VARCHAR(64)` | NO |  | 正規化した要求本文のSHA-256。 |
| `response_payload` | `TEXT` | NO |  | 元の成功応答のJSON。 |
| `expires_at` | `TIMESTAMPTZ` | NO |  | 成功記録の有効期限。 |

## テーブル制約

- `PRIMARY KEY (principal_id, idempotency_key)`

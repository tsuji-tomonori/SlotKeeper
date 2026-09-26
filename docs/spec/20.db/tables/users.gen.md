# users

予約を作成した利用者を表す。認証情報や個人属性は保存しない。

| カラム | 型 | NULL許可 | キー | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `principal_id` | `VARCHAR(200)` | NO | PK | 認証基盤のsubject。 |
| `first_seen_at` | `TIMESTAMPTZ` | NO |  | 初めて予約した日時。 |

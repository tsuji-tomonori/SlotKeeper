# API×保存先 CRUDマトリクス

行はOpenAPI summaryのAPI和名（operationId順）、列は保存先の完全名順。
DBテーブルはschema付き名、DB以外のidentity保存先も列に含める。
C: 作成、R: 参照、U: 更新、D: 削除。空欄はアクセスなし。

| API和名 | identity.jwks_signing_key | slotkeeper.idempotency_records | slotkeeper.reservation_events | slotkeeper.reservations | slotkeeper.resources | slotkeeper.users |
|---|---|---|---|---|---|---|
| 予約を取消す | R |  | C | RU | U |  |
| 予約を作成する | R | CRD | C | CR | U | C |
| 資源を登録する | R |  |  |  | C |  |
| 予約詳細を取得する | R |  | R | R |  |  |
| 予約表を取得する | R |  |  | R | R |  |
| 自分の予約一覧を取得する | R |  |  | R |  |  |
| 資源一覧を取得する | R |  |  |  | R |  |
| 資源を編集する | R |  |  | R | U |  |

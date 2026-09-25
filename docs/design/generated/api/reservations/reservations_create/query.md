# reservations_create / Query

## control

### SQL種別

update

### SQLの概要

資源の内部版を進め同じ資源の変更を競合させる。

### 利用するテーブル

resources

### 引数

params: id:str

### 戻り値

result: Resource

### 条件

```sql
-- 資源の内部版を進め同じ資源の変更を競合させる。
-- params: id:str
-- result: Resource
UPDATE slotkeeper.resources SET control_version=control_version+1 WHERE id=%(id)s RETURNING id, name, description, kind, active, version
```

## create

### SQL種別

insert

### SQLの概要

予約を確定状態で登録する。

### 利用するテーブル

reservations

### 引数

params: id:str, resource_id:str, subject:str, start_at:datetime, end_at:datetime, purpose:str

### 戻り値

result: Reservation

### 条件

```sql
-- 予約を確定状態で登録する。
-- params: id:str, resource_id:str, subject:str, start_at:datetime, end_at:datetime, purpose:str
-- result: Reservation
INSERT INTO slotkeeper.reservations(id,resource_id,subject,start_at,end_at,purpose,status,version) VALUES (%(id)s,%(resource_id)s,%(subject)s,%(start_at)s,%(end_at)s,%(purpose)s,'confirmed',1) RETURNING id, resource_id, subject, start_at, end_at, purpose, status, version
```

## event

### SQL種別

insert

### SQLの概要

予約操作の履歴を登録する。

### 利用するテーブル

reservation_events

### 引数

params: id:str, reservation_id:str, actor:str, action:str, at:datetime

### 戻り値

result: none

### 条件

```sql
-- 予約操作の履歴を登録する。
-- params: id:str, reservation_id:str, actor:str, action:str, at:datetime
-- result: none
INSERT INTO slotkeeper.reservation_events(id,reservation_id,actor,action,at) VALUES (%(id)s,%(reservation_id)s,%(actor)s,%(action)s,%(at)s)
```

## expire

### SQL種別

delete

### SQLの概要

期限を確認済みの要求記録を削除する。

### 利用するテーブル

idempotency_records

### 引数

params: subject:str, key:str

### 戻り値

result: none

### 条件

```sql
-- 期限を確認済みの要求記録を削除する。
-- params: subject:str, key:str
-- result: none
DELETE FROM slotkeeper.idempotency_records WHERE subject=%(subject)s AND request_key=%(key)s
```

## overlap

### SQL種別

select

### SQLの概要

取消済みを除いて半開区間の重複を調べる。

### 利用するテーブル

reservations

### 引数

params: resource_id:str, start:datetime, end:datetime

### 戻り値

result: Count

### 条件

```sql
-- 取消済みを除いて半開区間の重複を調べる。
-- params: resource_id:str, start:datetime, end:datetime
-- result: Count
SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%(resource_id)s AND status='confirmed' AND start_at<%(end)s AND end_at>%(start)s
```

## record

### SQL種別

insert

### SQLの概要

元の成功応答を要求キーと同じトランザクションで保存する。

### 利用するテーブル

idempotency_records

### 引数

params: subject:str, key:str, input_hash:str, response:str, expires_at:datetime

### 戻り値

result: none

### 条件

```sql
-- 元の成功応答を要求キーと同じトランザクションで保存する。
-- params: subject:str, key:str, input_hash:str, response:str, expires_at:datetime
-- result: none
INSERT INTO slotkeeper.idempotency_records(subject,request_key,input_hash,response,expires_at) VALUES (%(subject)s,%(key)s,%(input_hash)s,%(response)s,%(expires_at)s)
```

## replay

### SQL種別

select

### SQLの概要

要求の成功記録を利用者とキーで取得する。

### 利用するテーブル

idempotency_records

### 引数

params: subject:str, key:str

### 戻り値

result: Record

### 条件

```sql
-- 要求の成功記録を利用者とキーで取得する。
-- params: subject:str, key:str
-- result: Record
SELECT input_hash,response,expires_at FROM slotkeeper.idempotency_records WHERE subject=%(subject)s AND request_key=%(key)s
```

## user

### SQL種別

insert

### SQLの概要

初めて予約する利用者の業務属性を記録する。

### 利用するテーブル

users

### 引数

params: subject:str, now:datetime

### 戻り値

result: none

### 条件

```sql
-- 初めて予約する利用者の業務属性を記録する。
-- params: subject:str, now:datetime
-- result: none
INSERT INTO slotkeeper.users(subject,first_seen) VALUES (%(subject)s,%(now)s) ON CONFLICT(subject) DO NOTHING
```

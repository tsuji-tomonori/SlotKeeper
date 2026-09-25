# reservations_cancel / Query

## cancel

### SQL種別

update

### SQLの概要

予約を取消状態にして版を進める。

### 利用するテーブル

reservations

### 引数

params: id:str

### 戻り値

result: Reservation

### 条件

```sql
-- 予約を取消状態にして版を進める。
-- params: id:str
-- result: Reservation
UPDATE slotkeeper.reservations SET status='cancelled',version=version+1 WHERE id=%(id)s RETURNING id, resource_id, subject, start_at, end_at, purpose, status, version
```

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

## get

### SQL種別

select

### SQLの概要

指定した予約を取得する。

### 利用するテーブル

reservations

### 引数

params: id:str

### 戻り値

result: Reservation

### 条件

```sql
-- 指定した予約を取得する。
-- params: id:str
-- result: Reservation
SELECT id, resource_id, subject, start_at, end_at, purpose, status, version FROM slotkeeper.reservations WHERE id=%(id)s
```

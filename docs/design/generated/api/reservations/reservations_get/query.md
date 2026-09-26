# reservations_get / Query

## events

### SQL種別

select

### SQLの概要

予約の作成と取消の履歴を取得する。

### 利用するテーブル

reservation_events

### 引数

params: id:str

### 戻り値

result: Event

### 条件

```sql
-- 予約の作成と取消の履歴を取得する。
-- params: id:str
-- result: Event
SELECT id,reservation_id,actor,action,at FROM slotkeeper.reservation_events WHERE reservation_id=%(id)s ORDER BY at,id
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

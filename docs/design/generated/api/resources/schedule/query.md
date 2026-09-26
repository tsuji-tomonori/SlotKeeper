# schedule / Query

## bookings

### SQL種別

select

### SQLの概要

日本時間の一日内に開始する予約を取得する。

### 利用するテーブル

reservations

### 引数

params: id:str, start:datetime, end:datetime, limit:int, offset:int

### 戻り値

result: Reservation

### 条件

```sql
-- 日本時間の一日内に開始する予約を取得する。
-- params: id:str, start:datetime, end:datetime, limit:int, offset:int
-- result: Reservation
SELECT id, resource_id, subject, start_at, end_at, purpose, status, version FROM slotkeeper.reservations WHERE resource_id=%(id)s AND status='confirmed' AND start_at>=%(start)s AND start_at<%(end)s ORDER BY start_at,id LIMIT %(limit)s OFFSET %(offset)s
```

## resource

### SQL種別

select

### SQLの概要

資源の存在を確認する。

### 利用するテーブル

resources

### 引数

params: id:str

### 戻り値

result: Resource

### 条件

```sql
-- 資源の存在を確認する。
-- params: id:str
-- result: Resource
SELECT id, name, description, kind, active, version FROM slotkeeper.resources WHERE id=%(id)s
```

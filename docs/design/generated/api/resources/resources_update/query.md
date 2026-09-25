# resources_update / Query

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

## future

### SQL種別

select

### SQLの概要

開始前の確定予約を数える。

### 利用するテーブル

reservations

### 引数

params: id:str, now:datetime

### 戻り値

result: Count

### 条件

```sql
-- 開始前の確定予約を数える。
-- params: id:str, now:datetime
-- result: Count
SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%(id)s AND status='confirmed' AND start_at>%(now)s
```

## update

### SQL種別

update

### SQLの概要

資源を編集し公開版を進める。

### 利用するテーブル

resources

### 引数

params: id:str, name:str, description:str, kind:str, active:bool

### 戻り値

result: Resource

### 条件

```sql
-- 資源を編集し公開版を進める。
-- params: id:str, name:str, description:str, kind:str, active:bool
-- result: Resource
UPDATE slotkeeper.resources SET name=%(name)s,description=%(description)s,kind=%(kind)s,active=%(active)s,version=version+1 WHERE id=%(id)s RETURNING id, name, description, kind, active, version
```

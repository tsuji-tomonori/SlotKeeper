# resources_list / Query

## select_page

### SQL種別

select

### SQLの概要

資源を名前とIDの順で取得する。

### 利用するテーブル

resources

### 引数

params: limit:int, offset:int

### 戻り値

result: Resource

### 条件

```sql
-- 資源を名前とIDの順で取得する。
-- params: limit:int, offset:int
-- result: Resource
SELECT id, name, description, kind, active, version FROM slotkeeper.resources ORDER BY name, id LIMIT %(limit)s OFFSET %(offset)s
```

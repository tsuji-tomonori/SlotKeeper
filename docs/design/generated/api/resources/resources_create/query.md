# resources_create / Query

## create

### SQL種別

insert

### SQLの概要

有効な資源を登録する。

### 利用するテーブル

resources

### 引数

params: id:str, name:str, description:str, kind:str

### 戻り値

result: Resource

### 条件

```sql
-- 有効な資源を登録する。
-- params: id:str, name:str, description:str, kind:str
-- result: Resource
INSERT INTO slotkeeper.resources(id,name,description,kind,active,version,control_version) VALUES (%(id)s,%(name)s,%(description)s,%(kind)s,true,1,0) RETURNING id, name, description, kind, active, version
```

-- 資源を編集し公開版を進める。
-- params: id:str, name:str, description:str, kind:str, active:bool
-- result: Resource
UPDATE slotkeeper.resources SET name=%(name)s,description=%(description)s,kind=%(kind)s,active=%(active)s,version=version+1 WHERE id=%(id)s RETURNING id, name, description, kind, active, version

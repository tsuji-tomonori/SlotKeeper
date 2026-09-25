-- 資源の存在を確認する。
-- params: id:str
-- result: Resource
SELECT id, name, description, kind, active, version FROM slotkeeper.resources WHERE id=%(id)s

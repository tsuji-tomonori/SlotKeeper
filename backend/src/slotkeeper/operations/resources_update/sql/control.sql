-- 資源の内部版を進め同じ資源の変更を競合させる。
-- params: id:str
-- result: Resource
UPDATE slotkeeper.resources SET control_version=control_version+1 WHERE id=%(id)s RETURNING id, name, description, kind, active, version

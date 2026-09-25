-- 資源を名前とIDの順で取得する。
-- params: limit:int, offset:int
-- result: Resource
SELECT id, name, description, kind, active, version FROM slotkeeper.resources ORDER BY name, id LIMIT %(limit)s OFFSET %(offset)s

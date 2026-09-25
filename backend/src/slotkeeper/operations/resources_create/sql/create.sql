-- 有効な資源を登録する。
-- params: id:str, name:str, description:str, kind:str
-- result: Resource
INSERT INTO slotkeeper.resources(id,name,description,kind,active,version,control_version) VALUES (%(id)s,%(name)s,%(description)s,%(kind)s,true,1,0) RETURNING id, name, description, kind, active, version

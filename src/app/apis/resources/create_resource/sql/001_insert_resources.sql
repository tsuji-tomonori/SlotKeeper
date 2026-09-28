-- 管理者が登録した資源を有効な初期版で保存する。
INSERT INTO slotkeeper.resources (
    resource_id,
    name,
    description,
    kind,
    active,
    row_version,
    control_version
)
VALUES (
    @resource_id,
    @name,
    @description,
    @kind,
    TRUE,
    1,
    0
)
RETURNING resource_id, name, description, kind, active, row_version;

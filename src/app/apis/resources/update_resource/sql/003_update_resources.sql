-- 資源の名前・説明・種別・有効状態を更新し、公開版を1つ進める。
UPDATE slotkeeper.resources
SET
    name = @name,
    description = @description,
    kind = @kind,
    active = @active,
    row_version = row_version + 1
WHERE resource_id = @resource_id
RETURNING resource_id, name, description, kind, active, row_version;

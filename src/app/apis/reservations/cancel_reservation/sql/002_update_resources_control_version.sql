-- 同一資源の再予約と取消を競合させるため、資源の内部制御版を進めて現在値を取得する。
UPDATE slotkeeper.resources
SET control_version = control_version + 1
WHERE resource_id = @resource_id
RETURNING resource_id, active, row_version;

-- 予約表の対象資源が存在することを確認するため、資源IDを取得する。
SELECT r.resource_id
FROM slotkeeper.resources AS r
WHERE r.resource_id = @resource_id;

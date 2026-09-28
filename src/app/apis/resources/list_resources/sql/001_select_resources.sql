-- 資源一覧を返すため、名前とIDの固定順で継続位置より後の資源を取得する。
SELECT
    r.resource_id,
    r.name,
    r.description,
    r.kind,
    r.active,
    r.row_version
FROM slotkeeper.resources AS r
WHERE (
    CAST(@after_name AS VARCHAR) IS NULL
    OR CAST(@after_resource_id AS VARCHAR) IS NULL
    OR (r.name, r.resource_id) > (CAST(@after_name AS VARCHAR), CAST(@after_resource_id AS VARCHAR))
)
ORDER BY r.name, r.resource_id
LIMIT CAST(@limit AS INTEGER);

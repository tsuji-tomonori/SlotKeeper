-- 予約詳細を返すため、指定した予約を取得する。
SELECT
    rv.reservation_id,
    rv.resource_id,
    rv.owner_principal_id,
    rv.start_at,
    rv.end_at,
    rv.purpose,
    rv.status,
    rv.row_version
FROM slotkeeper.reservations AS rv
WHERE rv.reservation_id = @reservation_id;

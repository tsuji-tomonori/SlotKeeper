-- 指定日の予約表を返すため、日付範囲に重なる確定予約を開始日時とIDの順に取得する。
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
WHERE rv.resource_id = @resource_id
  AND rv.status = 'confirmed'
  AND rv.start_at < @day_end
  AND rv.end_at > @day_start
  AND (
      CAST(@after_start_at AS TIMESTAMPTZ) IS NULL
      OR CAST(@after_reservation_id AS VARCHAR) IS NULL
      OR (rv.start_at, rv.reservation_id)
      > (CAST(@after_start_at AS TIMESTAMPTZ), CAST(@after_reservation_id AS VARCHAR))
  )
ORDER BY rv.start_at, rv.reservation_id
LIMIT CAST(@limit AS INTEGER);

-- 自分の予約一覧を返すため、日付・状態・将来予約の条件で開始日時とIDの順に取得する。
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
WHERE rv.owner_principal_id = @owner_principal_id
  AND rv.start_at < @range_end
  AND rv.end_at > @range_start
  AND (CAST(@status AS VARCHAR) IS NULL OR rv.status = @status)
  AND (
      NOT CAST(@future_only AS BOOLEAN)
      OR (rv.status = 'confirmed' AND rv.start_at > @now)
  )
  AND (
      CAST(@after_start_at AS TIMESTAMPTZ) IS NULL
      OR CAST(@after_reservation_id AS VARCHAR) IS NULL
      OR (rv.start_at, rv.reservation_id)
      > (CAST(@after_start_at AS TIMESTAMPTZ), CAST(@after_reservation_id AS VARCHAR))
  )
ORDER BY rv.start_at, rv.reservation_id
LIMIT CAST(@limit AS INTEGER);

-- 予約枠の重複を判定するため、取消済みを除き半開区間が重なる確定予約の件数を取得する。
SELECT COUNT(*) AS overlapping_reservation_count
FROM slotkeeper.reservations AS rv
WHERE rv.resource_id = @resource_id
  AND rv.status = 'confirmed'
  AND rv.start_at < @end_at
  AND rv.end_at > @start_at;

-- 資源の無効化可否を判定するため、開始前の確定予約の件数を取得する。
SELECT COUNT(*) AS future_reservation_count
FROM slotkeeper.reservations AS rv
WHERE rv.resource_id = @resource_id
  AND rv.status = 'confirmed'
  AND rv.start_at > @now;

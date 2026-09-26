-- 予約詳細の履歴を返すため、作成と取消の履歴を発生順に取得する。
SELECT
    re.event_id,
    re.reservation_id,
    re.actor_principal_id,
    re.action,
    re.occurred_at
FROM slotkeeper.reservation_events AS re
WHERE re.reservation_id = @reservation_id
ORDER BY re.occurred_at, re.event_id;

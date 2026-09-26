-- 予約取消の履歴を取消と同じtransactionで追記する。
INSERT INTO slotkeeper.reservation_events (
    event_id,
    reservation_id,
    actor_principal_id,
    action,
    occurred_at
)
VALUES (@event_id, @reservation_id, @actor_principal_id, 'cancelled', @occurred_at);

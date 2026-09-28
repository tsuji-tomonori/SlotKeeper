-- 予約作成の履歴を予約と同じtransactionで追記する。
INSERT INTO slotkeeper.reservation_events (
    event_id,
    reservation_id,
    actor_principal_id,
    action,
    occurred_at
)
VALUES (@event_id, @reservation_id, @actor_principal_id, 'created', @occurred_at);

-- 予約を確定状態の初期版で保存する。
INSERT INTO slotkeeper.reservations (
    reservation_id,
    resource_id,
    owner_principal_id,
    start_at,
    end_at,
    purpose,
    status,
    row_version
)
VALUES (
    @reservation_id,
    @resource_id,
    @owner_principal_id,
    @start_at,
    @end_at,
    @purpose,
    'confirmed',
    1
)
RETURNING
    reservation_id,
    resource_id,
    owner_principal_id,
    start_at,
    end_at,
    purpose,
    status,
    row_version;

-- 予約を取消状態へ変更し、版を1つ進める。
UPDATE slotkeeper.reservations
SET
    status = 'cancelled',
    row_version = row_version + 1
WHERE reservation_id = @reservation_id
RETURNING
    reservation_id,
    resource_id,
    owner_principal_id,
    start_at,
    end_at,
    purpose,
    status,
    row_version;

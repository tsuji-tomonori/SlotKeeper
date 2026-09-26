-- 予約を取消状態にして版を進める。
-- params: id:str
-- result: Reservation
UPDATE slotkeeper.reservations SET status='cancelled',version=version+1 WHERE id=%(id)s RETURNING id, resource_id, subject, start_at, end_at, purpose, status, version

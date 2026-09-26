-- 指定した予約を取得する。
-- params: id:str
-- result: Reservation
SELECT id, resource_id, subject, start_at, end_at, purpose, status, version FROM slotkeeper.reservations WHERE id=%(id)s

-- 日本時間の一日内に開始する予約を取得する。
-- params: id:str, start:datetime, end:datetime, limit:int, offset:int
-- result: Reservation
SELECT id, resource_id, subject, start_at, end_at, purpose, status, version FROM slotkeeper.reservations WHERE resource_id=%(id)s AND status='confirmed' AND start_at>=%(start)s AND start_at<%(end)s ORDER BY start_at,id LIMIT %(limit)s OFFSET %(offset)s

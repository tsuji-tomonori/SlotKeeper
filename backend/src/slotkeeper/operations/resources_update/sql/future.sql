-- 開始前の確定予約を数える。
-- params: id:str, now:datetime
-- result: Count
SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%(id)s AND status='confirmed' AND start_at>%(now)s

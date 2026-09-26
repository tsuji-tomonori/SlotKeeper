-- 取消済みを除いて半開区間の重複を調べる。
-- params: resource_id:str, start:datetime, end:datetime
-- result: Count
SELECT count(*) AS count FROM slotkeeper.reservations WHERE resource_id=%(resource_id)s AND status='confirmed' AND start_at<%(end)s AND end_at>%(start)s

-- 本人の予約を期間と状態で絞り込む。
-- params: subject:str, start:datetime, end:datetime, state:str, future:bool, now:datetime, limit:int, offset:int
-- result: Reservation
SELECT id, resource_id, subject, start_at, end_at, purpose, status, version FROM slotkeeper.reservations WHERE subject=%(subject)s AND start_at>=%(start)s AND start_at<%(end)s AND (%(state)s='' OR status=%(state)s) AND (NOT %(future)s OR (status='confirmed' AND start_at>%(now)s)) ORDER BY start_at,id LIMIT %(limit)s OFFSET %(offset)s

-- 予約を確定状態で登録する。
-- params: id:str, resource_id:str, subject:str, start_at:datetime, end_at:datetime, purpose:str
-- result: Reservation
INSERT INTO slotkeeper.reservations(id,resource_id,subject,start_at,end_at,purpose,status,version) VALUES (%(id)s,%(resource_id)s,%(subject)s,%(start_at)s,%(end_at)s,%(purpose)s,'confirmed',1) RETURNING id, resource_id, subject, start_at, end_at, purpose, status, version

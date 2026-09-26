-- 予約操作の履歴を登録する。
-- params: id:str, reservation_id:str, actor:str, action:str, at:datetime
-- result: none
INSERT INTO slotkeeper.reservation_events(id,reservation_id,actor,action,at) VALUES (%(id)s,%(reservation_id)s,%(actor)s,%(action)s,%(at)s)

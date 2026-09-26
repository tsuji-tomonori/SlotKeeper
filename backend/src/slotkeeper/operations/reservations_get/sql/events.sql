-- 予約の作成と取消の履歴を取得する。
-- params: id:str
-- result: Event
SELECT id,reservation_id,actor,action,at FROM slotkeeper.reservation_events WHERE reservation_id=%(id)s ORDER BY at,id

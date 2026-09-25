-- 期限を確認済みの要求記録を削除する。
-- params: subject:str, key:str
-- result: none
DELETE FROM slotkeeper.idempotency_records WHERE subject=%(subject)s AND request_key=%(key)s

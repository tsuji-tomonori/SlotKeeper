-- 要求の成功記録を利用者とキーで取得する。
-- params: subject:str, key:str
-- result: Record
SELECT input_hash,response,expires_at FROM slotkeeper.idempotency_records WHERE subject=%(subject)s AND request_key=%(key)s

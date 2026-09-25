-- 元の成功応答を要求キーと同じトランザクションで保存する。
-- params: subject:str, key:str, input_hash:str, response:str, expires_at:datetime
-- result: none
INSERT INTO slotkeeper.idempotency_records(subject,request_key,input_hash,response,expires_at) VALUES (%(subject)s,%(key)s,%(input_hash)s,%(response)s,%(expires_at)s)

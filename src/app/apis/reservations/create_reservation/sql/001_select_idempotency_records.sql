-- 予約作成要求の再送を照合するため、利用者とIdempotency-Keyの成功記録を取得する。
SELECT
    ir.idempotency_key,
    ir.request_hash,
    ir.response_payload,
    ir.expires_at
FROM slotkeeper.idempotency_records AS ir
WHERE ir.principal_id = @principal_id
  AND ir.idempotency_key = @idempotency_key;

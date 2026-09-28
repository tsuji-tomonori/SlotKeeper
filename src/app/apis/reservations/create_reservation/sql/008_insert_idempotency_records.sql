-- 元の成功応答を予約と同じtransactionで24時間の成功記録として保存する。
INSERT INTO slotkeeper.idempotency_records (
    principal_id,
    idempotency_key,
    request_hash,
    response_payload,
    expires_at
)
VALUES (@principal_id, @idempotency_key, @request_hash, @response_payload, @expires_at);

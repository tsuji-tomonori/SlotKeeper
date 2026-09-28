-- 有効期限を過ぎた成功記録を新規要求として扱うため削除する。
DELETE FROM slotkeeper.idempotency_records
WHERE principal_id = @principal_id
  AND idempotency_key = @idempotency_key;

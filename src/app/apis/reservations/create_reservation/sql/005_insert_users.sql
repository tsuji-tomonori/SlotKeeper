-- 初めて予約する利用者を記録する。既存利用者は変更しない。
INSERT INTO slotkeeper.users (principal_id, first_seen_at)
VALUES (@principal_id, @first_seen_at)
ON CONFLICT (principal_id) DO NOTHING;

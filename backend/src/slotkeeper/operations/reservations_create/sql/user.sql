-- 初めて予約する利用者の業務属性を記録する。
-- params: subject:str, now:datetime
-- result: none
INSERT INTO slotkeeper.users(subject,first_seen) VALUES (%(subject)s,%(now)s) ON CONFLICT(subject) DO NOTHING

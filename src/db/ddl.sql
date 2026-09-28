CREATE SCHEMA IF NOT EXISTS slotkeeper;

CREATE TABLE IF NOT EXISTS slotkeeper.resources (
    resource_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- noqa: RF04
    description VARCHAR(1000) NOT NULL, -- noqa: RF04
    kind VARCHAR(20) NOT NULL,
    active BOOLEAN NOT NULL,
    row_version INTEGER NOT NULL,
    control_version BIGINT NOT NULL
);

-- COMMENT ON TABLE slotkeeper.resources IS '予約対象となる会議室または備品を表す。無効化しても既存予約の記録は保持する。';
-- COMMENT ON COLUMN slotkeeper.resources.resource_id IS '資源ID。';
-- COMMENT ON COLUMN slotkeeper.resources.name IS '資源名。空白除去後1〜100文字。';
-- COMMENT ON COLUMN slotkeeper.resources.description IS '資源の説明。0〜1,000文字。';
-- COMMENT ON COLUMN slotkeeper.resources.kind IS '資源種別。roomまたはequipment。';
-- COMMENT ON COLUMN slotkeeper.resources.active IS '新規予約を受け付けるかどうか。';
-- COMMENT ON COLUMN slotkeeper.resources.row_version IS '利用者に公開する楽観ロック用の行バージョン。';
-- COMMENT ON COLUMN slotkeeper.resources.control_version IS '同一資源の予約作成・取消・無効化を競合させる内部制御版。';

CREATE TABLE IF NOT EXISTS slotkeeper.users (
    principal_id VARCHAR(200) PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL
);

-- COMMENT ON TABLE slotkeeper.users IS '予約を作成した利用者を表す。認証情報や個人属性は保存しない。';
-- COMMENT ON COLUMN slotkeeper.users.principal_id IS '認証基盤のsubject。';
-- COMMENT ON COLUMN slotkeeper.users.first_seen_at IS '初めて予約した日時。';

CREATE TABLE IF NOT EXISTS slotkeeper.reservations (
    reservation_id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(36) NOT NULL, -- REFERENCES slotkeeper.resources (resource_id)
    owner_principal_id VARCHAR(200) NOT NULL, -- REFERENCES slotkeeper.users (principal_id)
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    row_version INTEGER NOT NULL
);

-- COMMENT ON TABLE slotkeeper.reservations IS '資源の予約を表す。予約区間は[開始,終了)で、状態はconfirmedからcancelledへだけ遷移する。';
-- COMMENT ON COLUMN slotkeeper.reservations.reservation_id IS '予約ID。';
-- COMMENT ON COLUMN slotkeeper.reservations.resource_id IS '予約対象の資源ID。';
-- COMMENT ON COLUMN slotkeeper.reservations.owner_principal_id IS '予約者の認証subject。';
-- COMMENT ON COLUMN slotkeeper.reservations.start_at IS '予約開始日時。UTCで保存する。';
-- COMMENT ON COLUMN slotkeeper.reservations.end_at IS '予約終了日時。UTCで保存し、この時刻を含まない。';
-- COMMENT ON COLUMN slotkeeper.reservations.purpose IS '予約目的。1〜200文字。本人と管理者だけに返す。';
-- COMMENT ON COLUMN slotkeeper.reservations.status IS '予約状態。confirmedまたはcancelled。';
-- COMMENT ON COLUMN slotkeeper.reservations.row_version IS '楽観ロック用の行バージョン。';

CREATE TABLE IF NOT EXISTS slotkeeper.reservation_events (
    event_id VARCHAR(36) PRIMARY KEY,
    reservation_id VARCHAR(36) NOT NULL, -- REFERENCES slotkeeper.reservations (reservation_id)
    actor_principal_id VARCHAR(200) NOT NULL,
    action VARCHAR(20) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL
);

-- COMMENT ON TABLE slotkeeper.reservation_events IS '予約の作成と取消の履歴を表す。予約の変更と同じtransactionで追記する。';
-- COMMENT ON COLUMN slotkeeper.reservation_events.event_id IS '履歴ID。';
-- COMMENT ON COLUMN slotkeeper.reservation_events.reservation_id IS '対象の予約ID。';
-- COMMENT ON COLUMN slotkeeper.reservation_events.actor_principal_id IS '操作した利用者の認証subject。';
-- COMMENT ON COLUMN slotkeeper.reservation_events.action IS '操作種別。createdまたはcancelled。';
-- COMMENT ON COLUMN slotkeeper.reservation_events.occurred_at IS '操作日時。';

CREATE TABLE IF NOT EXISTS slotkeeper.idempotency_records (
    principal_id VARCHAR(200) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    response_payload TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (principal_id, idempotency_key)
);

-- COMMENT ON TABLE slotkeeper.idempotency_records IS '予約作成要求の成功記録を表す。利用者とIdempotency-Keyの組で24時間有効。';
-- COMMENT ON COLUMN slotkeeper.idempotency_records.principal_id IS '要求した利用者の認証subject。';
-- COMMENT ON COLUMN slotkeeper.idempotency_records.idempotency_key IS 'Idempotency-Keyヘッダの値。';
-- COMMENT ON COLUMN slotkeeper.idempotency_records.request_hash IS '正規化した要求本文のSHA-256。';
-- COMMENT ON COLUMN slotkeeper.idempotency_records.response_payload IS '元の成功応答のJSON。';
-- COMMENT ON COLUMN slotkeeper.idempotency_records.expires_at IS '成功記録の有効期限。';

CREATE INDEX IF NOT EXISTS reservation_resource_time ON slotkeeper.reservations (resource_id, start_at);
CREATE INDEX IF NOT EXISTS reservation_owner_time ON slotkeeper.reservations (owner_principal_id, start_at);
CREATE INDEX IF NOT EXISTS event_reservation ON slotkeeper.reservation_events (reservation_id, occurred_at);

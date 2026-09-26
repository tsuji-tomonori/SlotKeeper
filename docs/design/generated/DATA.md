# データ設計

## 資源 / resources

| 和名 | 物理名 | 型 | NULL | PK |
| --- | --- | --- | --- | --- |
| 資源ID | id | VARCHAR(36) | False | True |
| 資源名 | name | VARCHAR(100) | False | False |
| 説明 | description | VARCHAR(1000) | False | False |
| 種類 | kind | VARCHAR(20) | False | False |
| 有効 | active | BOOLEAN | False | False |
| 公開版 | version | INT | False | False |
| 競合制御版 | control_version | BIGINT | False | False |

```sql
CREATE TABLE IF NOT EXISTS slotkeeper.resources (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(1000) NOT NULL,
  kind VARCHAR(20) NOT NULL,
  active BOOLEAN NOT NULL,
  version INT NOT NULL,
  control_version BIGINT NOT NULL
);
```

## 利用者 / users

| 和名 | 物理名 | 型 | NULL | PK |
| --- | --- | --- | --- | --- |
| 認証subject | subject | VARCHAR(200) | False | True |
| 初回利用時刻 | first_seen | TIMESTAMPTZ | False | False |

```sql
CREATE TABLE IF NOT EXISTS slotkeeper.users (
  subject VARCHAR(200) PRIMARY KEY,
  first_seen TIMESTAMPTZ NOT NULL
);
```

## 予約 / reservations

| 和名 | 物理名 | 型 | NULL | PK |
| --- | --- | --- | --- | --- |
| 予約ID | id | VARCHAR(36) | False | True |
| 資源ID | resource_id | VARCHAR(36) | False | False |
| 予約者 | subject | VARCHAR(200) | False | False |
| 開始日時 | start_at | TIMESTAMPTZ | False | False |
| 終了日時 | end_at | TIMESTAMPTZ | False | False |
| 目的 | purpose | VARCHAR(200) | False | False |
| 状態 | status | VARCHAR(20) | False | False |
| 版 | version | INT | False | False |

```sql
CREATE TABLE IF NOT EXISTS slotkeeper.reservations (
  id VARCHAR(36) PRIMARY KEY,
  resource_id VARCHAR(36) NOT NULL,
  subject VARCHAR(200) NOT NULL,
  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ NOT NULL,
  purpose VARCHAR(200) NOT NULL,
  status VARCHAR(20) NOT NULL,
  version INT NOT NULL
);
```

## 予約履歴 / reservation_events

| 和名 | 物理名 | 型 | NULL | PK |
| --- | --- | --- | --- | --- |
| 履歴ID | id | VARCHAR(36) | False | True |
| 予約ID | reservation_id | VARCHAR(36) | False | False |
| 操作者 | actor | VARCHAR(200) | False | False |
| 操作 | action | VARCHAR(20) | False | False |
| 操作日時 | at | TIMESTAMPTZ | False | False |

```sql
CREATE TABLE IF NOT EXISTS slotkeeper.reservation_events (
  id VARCHAR(36) PRIMARY KEY,
  reservation_id VARCHAR(36) NOT NULL,
  actor VARCHAR(200) NOT NULL,
  action VARCHAR(20) NOT NULL,
  at TIMESTAMPTZ NOT NULL
);
```

## 要求成功記録 / idempotency_records

| 和名 | 物理名 | 型 | NULL | PK |
| --- | --- | --- | --- | --- |
| 利用者 | subject | VARCHAR(200) | False | False |
| 要求キー | request_key | VARCHAR(128) | False | False |
| 正規化入力hash | input_hash | VARCHAR(64) | False | False |
| 元の成功応答 | response | TEXT | False | False |
| 有効期限 | expires_at | TIMESTAMPTZ | False | False |

```sql
CREATE TABLE IF NOT EXISTS slotkeeper.idempotency_records (
  subject VARCHAR(200) NOT NULL,
  request_key VARCHAR(128) NOT NULL,
  input_hash VARCHAR(64) NOT NULL,
  response TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (subject, request_key)
);
```

論理参照はbackend/logical-relations.jsonに宣言。物理FKは使用しない。

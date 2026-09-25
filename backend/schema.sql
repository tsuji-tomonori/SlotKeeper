CREATE SCHEMA IF NOT EXISTS slotkeeper;
CREATE TABLE IF NOT EXISTS slotkeeper.resources (
 id varchar(36) PRIMARY KEY,
 name varchar(100) NOT NULL,
 description varchar(1000) NOT NULL,
 kind varchar(20) NOT NULL,
 active boolean NOT NULL,
 version integer NOT NULL,
 control_version bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS slotkeeper.users (
 subject varchar(200) PRIMARY KEY,
 first_seen timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS slotkeeper.reservations (
 id varchar(36) PRIMARY KEY,
 resource_id varchar(36) NOT NULL,
 subject varchar(200) NOT NULL,
 start_at timestamptz NOT NULL,
 end_at timestamptz NOT NULL,
 purpose varchar(200) NOT NULL,
 status varchar(20) NOT NULL,
 version integer NOT NULL
);
CREATE TABLE IF NOT EXISTS slotkeeper.reservation_events (
 id varchar(36) PRIMARY KEY,
 reservation_id varchar(36) NOT NULL,
 actor varchar(200) NOT NULL,
 action varchar(20) NOT NULL,
 at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS slotkeeper.idempotency_records (
 subject varchar(200) NOT NULL,
 request_key varchar(128) NOT NULL,
 input_hash varchar(64) NOT NULL,
 response text NOT NULL,
 expires_at timestamptz NOT NULL,
 PRIMARY KEY(subject, request_key)
);

# 起動、配布、復旧

ローカルはREADMEのCompose入口を使用します。`verify-db`は試験用の独立DBで、通常の開発データに対するDROPやTRUNCATEは行いません。

## AWSへの配布

実AWSでの実行には明示したaccount・region・roleと一時認証情報が必要です。このリポジトリの初回構築では実デプロイしません。DBの削除保護とRETAINを有効にしています。先にdiffを確認します。

```bash
# 事前にCompose検証でLinux用ZIPを作る
# 認証情報は環境に一時的に渡し、ファイルをcommitしない
docker compose --profile test run --rm --entrypoint npx verify cdk synth --strict
docker compose --profile test run --rm --entrypoint npx verify cdk diff
docker compose --profile test run --rm --entrypoint npx verify cdk deploy --outputs-file artifacts/cdk-outputs.json
```

CDK出力のDsqlEndpointへ、初期設定用の `dsql:DbConnectAdmin` 権限を持つIAMロールで接続します。アプリは `slotkeeper_app` と `dsql:DbConnect` のみです。DDLを適用するmigrationロールは別に作成します。schema/索引は1DDL1transactionとし、非同期索引の完了を待ちます。

```sql
CREATE ROLE slotkeeper_migration WITH LOGIN;
CREATE ROLE slotkeeper_app WITH LOGIN;
-- 各ARNは認可済みの実IAM roleから指定する。以下は構文例。
AWS IAM GRANT slotkeeper_migration TO 'arn:aws:iam::ACCOUNT:role/MigrationRole';
AWS IAM GRANT slotkeeper_app TO 'arn:aws:iam::ACCOUNT:role/ApplicationRole';
CREATE SCHEMA slotkeeper AUTHORIZATION slotkeeper_migration;
GRANT USAGE ON SCHEMA slotkeeper TO slotkeeper_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA slotkeeper TO slotkeeper_app;
ALTER DEFAULT PRIVILEGES FOR ROLE slotkeeper_migration IN SCHEMA slotkeeper GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO slotkeeper_app;
```

DSQL設定（`SLOT_DATABASE_MODE=dsql`、`SLOT_ENVIRONMENT=aws`、`SLOT_DSQL_HOST`、`SLOT_DATABASE_USER=slotkeeper_migration`）を指定して `python -m tools.project.migrate` をコンテナ内で実行します。初期設定用権限を常時アプリへ付与しません。

```bash
docker compose --profile test run --rm --entrypoint python verify -m tools.project.deploy --outputs artifacts/cdk-outputs.json --publish
# 初期管理者にはCognitoから案内メールが送られる。実メール送信は別途明示した宛先で実行する。
docker compose --profile test run --rm --entrypoint python verify -m tools.project.deploy --outputs artifacts/cdk-outputs.json --admin-email ADMIN_EMAIL
```

## 復旧

アプリの前版ZIPと静的成果物はCI artifactから取得し、対応するrevisionのCDKでdiff後に再配置します。S3はversioningを使用します。DBの破壊的migrationを自動で戻しません。障害時は書込みを停止し、対象revision、要求ID、CloudWatchの操作・応答statusを確認します。予約目的やtokenをログ収集のために追加しません。

DSQLの実接続、IAM mapping、SQL互換、OCCは実AWSの受入環境で確認します。PostgreSQLのRepeatable Read成功をDSQLでの検証済みに読み替えません。

## 性能測定

```bash
docker compose --profile perf run --build --rm perf
```

資源100、利用者200、過去予約10万を合成IDで投入します。既存データは削除しません。20並列、参照80%・作成取消20%相当、2分ウォームアップと5分測定を3回です。結果は `artifacts/performance.json` で、通常の全検証とは別runです。

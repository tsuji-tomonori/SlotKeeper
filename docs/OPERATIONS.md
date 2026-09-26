# 起動、配布、復旧

ローカルはREADMEのCompose入口を使用します。`verify-db`は試験用の独立DBで、通常の開発データに対するDROPやTRUNCATEは行いません。

## AWSへの配布

実AWSでの実行には明示したaccount・region・roleと一時認証情報が必要です。このリポジトリの初回構築では実デプロイしません。DBの削除保護とRETAINを有効にしています。先にdiffを確認します。

```bash
# 事前にCompose検証でLinux用ZIPを作る
# 認証情報は環境に一時的に渡し、ファイルをcommitしない
docker compose --profile test run --rm --entrypoint npx verify cdk synth --strict -c env=dev
docker compose --profile test run --rm --entrypoint npx verify cdk diff -c env=dev
docker compose --profile test run --rm --entrypoint npx verify cdk deploy -c env=dev --outputs-file artifacts/cdk-outputs.json
```

環境ごとの公開可能な設定は `infra/environments/<env>.json`（dev/prod）にあります。未定義の環境名は合成前に拒否します。stack名は `SlotKeeper-<env>` です。秘密値はここに置かず、CDKのsynthはAWS認証情報もlive lookupも使いません。

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
docker compose --profile test run --rm --entrypoint python verify -m tools.project.deploy --outputs artifacts/cdk-outputs.json --stack SlotKeeper-dev --publish
# 初期管理者にはCognitoから案内メールが送られる。実メール送信は別途明示した宛先で実行する。
docker compose --profile test run --rm --entrypoint python verify -m tools.project.deploy --outputs artifacts/cdk-outputs.json --stack SlotKeeper-dev --admin-email ADMIN_EMAIL
```

`--publish` はCDK出力から `config.json`（API URL、issuer、client ID、Hosted UIのlogout URL）を作り、静的成果物をS3へ配置してCloudFrontの入口と設定をinvalidateします。利用者情報や秘密は埋め込みません。

## 設計・品質ポータルの公開

`.github/workflows/quality.yml` がPRと既定branchで同じ `verify` を実行します。既定branchへのpushだけが `site-ready` を満たすPages artifactを公開し、公開後にsmoke job（`e2e/portal-remote.config.ts`）が実URLのbase path・検索・図・DB探索を検査します。公開jobだけが `pages: write` と `id-token: write` を持ちます。ローカルで同じsmokeを行う場合:

```bash
docker compose --profile test run --rm --no-deps -e SLOT_PORTAL_URL=https://tsuji-tomonori.github.io/SlotKeeper/ --entrypoint npx verify playwright test --config=e2e/portal-remote.config.ts
```

## ログ確認

APIは1要求1行のJSON（`request_id`、`operation`、`status`、`elapsed_ms`）を出力します。応答ヘッダー `X-Request-ID` と照合します。予約目的・token・生の例外本文は出力しません。

```bash
docker compose logs api --since 10m
```

## 復旧

アプリの前版ZIPと静的成果物はCI artifactから取得し、対応するrevisionのCDKでdiff後に再配置します。S3はversioningを使用します。DBの破壊的migrationを自動で戻しません。障害時は書込みを停止し、対象revision、要求ID、CloudWatchの操作・応答statusを確認します。予約目的やtokenをログ収集のために追加しません。

DSQLの実接続、IAM mapping、SQL互換、OCCは実AWSの受入環境で確認します。PostgreSQLのRepeatable Read成功をDSQLでの検証済みに読み替えません。

## 性能測定

```bash
docker compose --profile perf run --build --rm perf
```

資源100、利用者200、過去予約10万を合成IDで投入します。既存データは削除しません。20並列、参照80%・作成取消20%相当、2分ウォームアップと5分測定を3回です。結果は `artifacts/performance.json` で、通常の全検証とは別runです。

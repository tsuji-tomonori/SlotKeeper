# SlotKeeper

会議室と備品の空き時間を確認し、予約と取消ができる日本語アプリです。Astroの静的画面、FastAPI、PostgreSQL（AWSはAurora DSQL）、Cognito/ローカルKeycloakで構成します。

開発標準は `5788b8671a74d08a230ade5d25c4719335cd7f71` に固定しています。初回版の受入範囲は [実装指示](IMPLEMENTATION_REQUEST.md)、永続要件の正本は [Quint](spec/requirements/requirements.qnt) です。受入条件と実在テストIDの対応は生成設計の [要件トレース](docs/spec/80.trace/trace.gen.md) で確認できます。

実装構成と設計文書は [lazunex](https://github.com/tsuji-tomonori/lazunex)（`096e1e580ab1c0670c57e4febad2bd9fdd4698ee`）を正として揃えています。差異と処置は [lazunexとの差異一覧](docs/spec/10.architecture/lazunex-alignment.manual.md) にあります。

## ローカルで使う

必要なものはGitとDocker Compose v2だけです。Windows 11ではWSL2とDocker Desktopを使用できます。ホストにPython・Node・AWS CLIは不要です。

```bash
git clone https://github.com/tsuji-tomonori/SlotKeeper.git
cd SlotKeeper
# 初回起動。DB migrationと開発用seedも依存関係として処理する
docker compose up --build --wait
```

[アプリ](http://localhost:4321)を開いてログインします。ローカル専用の合成ユーザーは `alice`、`bob`、`admin`、パスワードは全員 `Local-test-2026!` です。AWSには投入しません。

| URL | 用途 |
| --- | --- |
| http://localhost:4321 | アプリ（Astro静的build） |
| http://localhost:8000/docs | FastAPIのOpenAPI画面 |
| http://localhost:8080 | ローカルOIDC（Keycloak） |
| http://localhost:4173/SlotKeeper/ | 品質ポータル（`docs` profile） |

## 構成

```text
src/
  app/                       FastAPIアプリ（lazunex構成）
    main.py                  app生成、要求ID・運用ログmiddleware、/health
    apis/<group>/<operation>/ router.py / functions.py / schemas.py / samples.py / contract.py / sql/ / generated/queries.py
    core/ db/ integrations/  設定・運用ログ、SQL実行とOCC再試行、JWT検証provider
  db/ddl.sql                 DDL正本（slotkeeper schema、論理FK）
  tools/                     lazunex由来の生成器・検査器、rulecheck、project入口（verify/design/migrate等）
  app_tool/                  app-docs / app-codegen / app-archlint
docs/spec/                   10.architecture（手動）/ 20.db / 30.crud / 40.apis / 50.e2e / 60.frontend / 70.infra / 80.trace / tools
docs/rule/                   コーディング規約・rulecheck checklist・文書語彙
tests/                       app/apis/<group>/<operation>/test_router.py・test_functions.py、tools、infra、integrations
frontend/ portal/ e2e/ infra/
```

## Checks

Compose内の `verify` と同じ検査を、Python環境があればホストでも個別に実行できます（`uv sync` 後）。

```bash
uv run --locked ruff format --check src tests infra
uv run --locked ruff check src tests infra
uv run --locked pyright
uv run --locked mypy
SLOT_TEST_DB=1 uv run --locked pytest          # 専用のPostgreSQL（SLOT_DATABASE_URL）が必要
uv run app-codegen all --check                  # SQL→型付きquery
uv run app-docs generate --check                # lazunex形式の設計文書・E2E仕様・tools文書
uv run app-archlint all                         # API契約・sequence・単体テスト要因・E2E仕様
uv run python -m tools.rulecheck verify --repo-root . --rules-dir docs/rule/coding \
  --checklist docs/rule/coding/12_review_checklist.generated.md --config config/rulecheck_config.example.json
uv run python -m tools.project.rulecheck_gate   # MUST規約。既知負債はconfig/rulecheck_baseline.json
uv run python -B src/tools/project/design.py --manifest --check
python .agents/skills/generate-implementation-design/scripts/check_design.py --root .
```

生成物を更新するときは `uv run app-codegen all`、`uv run app-docs generate`、`uv run python -B src/tools/project/design.py --target all --manifest` の順に実行します（Composeでは `verify --generate-design`）。

## 検証と設計

```bash
# 全ローカル検証。異常系・生成設計・ポータル検証を含む
docker compose --profile test run --build --rm verify
# 検査対象を絞った日常実行（部分検証としてポータルに表示される）
docker compose --profile test run --rm verify --suite backend
docker compose --profile test run --rm verify --suite frontend
docker compose --profile test run --rm verify --suite infra
docker compose --profile test run --rm verify --suite e2e
docker compose --profile test run --rm verify --suite design
docker compose --profile test run --rm verify --suite portal
# 実装由来の設計・要件派生物・フロント型を明示的に更新する
docker compose --profile test run --rm verify --generate-design
# 性能測定（通常の全検証とは別run）
docker compose --profile perf run --build --rm perf
# 保存した品質ポータルを閲覧する
docker compose --profile docs up --build --wait docs
```

- 原本は `artifacts/`、公開allowlistは `artifacts/site/` です。失敗を含むポータルを作成してから、失敗があれば非0で終了します。
- 検証DB（`verify-db`、tmpfs）は開発DBと別サービスで、開発データを削除しません。
- `--generate-design` は専用のbind mountを通して生成物をホストへ書き戻します。通常の検証は生成物を上書きせず、欠落・変更・余剰（旧帳票）と要件traceの欠落を報告します。
- 受入条件IDはテスト説明（pytestのdocstring、Vitestのdescribe、Playwrightのtitle）に `[SLOT-AC03]` の形で付けます。要件にないIDや、要件の `traces.tests` にないテストfileからの参照は設計生成で拒否されます。

## 停止とリセット

```bash
# データを保持して停止する
docker compose down
# ローカル開発データを明示的に全削除する（復元できません）
docker compose down --volumes
# 再起動時にschemaとseedを準備する（seedは固定IDで重複しない）
docker compose up --build --wait
```

lazunex構成への移行で列名（`id`→`resource_id`等）が変わりました。移行前に作成したローカルDB volumeは `docker compose down --volumes` で作り直してください。

## AWSと公開

アプリ本体は非公開S3＋CloudFront OAC、HTTP API＋通常Lambda、Cognito、Aurora DSQL。Python CDKで定義し、`-c env=dev|prod` で [環境設定](infra/environments/) を選びます（既定はdev、リージョンは `ap-northeast-1`）。実AWS account・roleが未指定のため、本リポジトリではデプロイしていません。synth・ZIP検査と実AWS検証は別物です。手順は [運用書](docs/spec/10.architecture/operations.manual.md) にあります。

設計・品質ポータルの公開URL：<https://tsuji-tomonori.github.io/SlotKeeper/>。GitHub Actionsは同じCompose入口を実行し、既定branchへのpushだけからPagesへ公開し、公開後に実URLへsmoke testを行います。リポジトリ設定でPagesのsourceをGitHub Actionsにする必要があります。

## 整合性

予約区間は `[開始,終了)`。同一資源の作成・取消・無効化は内部制御版を更新し、DSQLのOCC/ローカルのRepeatable Readで競合させます。成功時の予約・履歴・要求キーは同一commit。一般利用者へ他人の目的・識別情報・履歴を返しません。開始前だけ取消できます。

認証tokenはブラウザのメモリのみ。ページ再読み込み時は再認証します。PKCEの一時stateだけをsessionStorageへ置きます。ログアウトではメモリのtokenを破棄し、Keycloakでは`id_token_hint`付きのend session、CognitoではHosted UIの`/logout`でsessionも終了します。

E2Eはverifyコンテナ内でlocalhostの4321/8000/8080を各サービスへTCP転送し、利用者のブラウザと同じissuer・callback URLで検証します。

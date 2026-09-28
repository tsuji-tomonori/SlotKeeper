# lazunexとの差異一覧

[lazunex](https://github.com/tsuji-tomonori/lazunex)（固定revision `096e1e580ab1c0670c57e4febad2bd9fdd4698ee`）を正とし、文書内容・CRUD図の書き方・実装構成の差異を洗い出した結果と処置を記録する。判断の要旨は [003-lazunex-alignment](decisions/003-lazunex-alignment.manual.md) を参照する。

処置の区分:

- **準拠**: lazunexの構成・書式へ変更した。
- **維持**: SlotKeeperの要件（`spec/requirements/requirements.qnt`）が別の選択を要求するため、lazunexと異なるまま残した。根拠の要件IDを付ける。
- **拡張**: lazunexの仕組みを採用したうえで、SlotKeeperの構成で必要になった機能を足した、またはlazunex側の不具合を直した。

## 1. リポジトリと実装構成

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| S01 | アプリ配置 | `src/app`（`main.py`・`local.py`・`core/`・`db/`・`apis/`・`integrations/`） | `backend/src/slotkeeper`（`app.py`・`auth.py`・`db.py`・`domain.py`・`settings.py`） | `src/app`へ移設し同じ分割にした | 準拠 |
| S02 | operation単位 | `apis/<group>/<operation>/`に`router.py`・`functions.py`・`schemas.py`・`samples.py`・`contract.py`・`queries.py`・`sql/`・`generated/` | `operations/<group>_<verb>/endpoint.py`と`sql/`だけ。業務規則は`domain.py`に集約 | 8 operationを分解し、operation名を`create_reservation`等へ変更 | 準拠 |
| S03 | operationId | camelCase（`createProject`） | snake_case（`reservations_create`） | camelCase（`createReservation`） | 準拠 |
| S04 | Routerの責務 | 処理順・分岐・例外・transactionをrouterが所有し、`api_functions.<name>`で個別処理を呼ぶ | endpoint関数に処理を直書き | routerへ処理順を集約し、`has_`/`is_`述語は`if`内で呼ぶ | 準拠 |
| S05 | 個別処理の記述 | docstring必須、`raise_missing_runtime_dependency`、`@resource-free`宣言 | docstringは任意 | 全関数に日本語docstringと資源利用の宣言 | 準拠 |
| S06 | 型付きquery | `sql/NNN_*.sql`（`@name`束縛）から`generated/queries.py`を生成し、`queries.py`は互換shim | `sql/*.sql`（`%(name)s`）と手書きの`query_models.py`、`tools/project/queries.py`で生成 | lazunex形式へ移行し、旧生成器を削除 | 準拠 |
| S07 | SQL方言 | MySQL（`asyncmy`） | PostgreSQL / Aurora DSQL（同期psycopg） | PostgreSQL / Aurora DSQLのまま、SQLAlchemy async + psycopgへ変更 | 維持（TECH-DB） |
| S08 | DB接続 | `create_async_engine` + `StaticPool` | 同期`psycopg`接続 | `create_async_engine` + `NullPool`、DSQLは公式connectorの`async_creator` | 準拠（pool方式はLambda向けに`NullPool`） |
| S09 | 同時更新 | MySQLのロック | Repeatable Read / DSQL OCCと手書き再試行 | `retry_transaction`デコレータでOCC競合（40001等）を再試行し、上限超過は503 | 維持（TECH-DB, COM-06） |
| S10 | DDL正本 | `src/db/ddl.sql`（物理FK、`COMMENT ON`） | `backend/schema.sql`・`indexes.sql`・`schema-labels.json`・`logical-relations.json` | `src/db/ddl.sql`へ統合。列説明は`-- COMMENT ON`、参照は`-- REFERENCES`の論理FK | 準拠（物理FKだけDSQL制約で論理FK） |
| S11 | 列名 | `<entity>_id`・`row_version`・`created_at`等 | `id`・`version`・`subject`・`first_seen` | `resource_id`・`row_version`・`owner_principal_id`・`first_seen_at`等へ変更 | 準拠 |
| S12 | 認証 | `X-Principal-Id`ヘッダ | Cognito/Keycloak JWT | JWTのまま、`integrations/identity`のport・provider・fakeへ分離 | 維持（TECH-AUTH） |
| S13 | 外部連携 | `integrations/<service>/`（port・provider・fake・deps）、boto3の管理API群 | `auth.py`に直接実装 | `integrations/identity/`だけをlazunex形式で追加。AWS管理APIは要件外のため非採用 | 準拠（範囲はSlotKeeper要件のみ） |
| S14 | 実行基盤 | uvicorn / Docker Compose | Lambda（Mangum）+ Compose | `src/app/lambda_handler.py`でMangumを維持 | 維持（TECH-LAMBDA） |
| S15 | 画面 | なし（API only） | Astro + React | 維持。API契約の変更（S20〜S23）へ追従 | 維持（TECH-STACK） |
| S16 | Python | 3.14、hatchling、`app-docs`/`app-codegen`/`app-archlint` | 3.12、package=false | 3.14、hatchling、3 scriptを導入 | 準拠 |
| S17 | 型・lint | ruff・pyright・mypy strict（`src`,`tests`） | ruff・pyright・mypy（`backend`等） | 対象を`src`・`tests`・`infra`へ変更。全件0 error | 準拠 |
| S18 | health | `main.py`の`/health`（規約ENTRYPOINT-DO-002） | `app.py`の`/health` | `main.py`の`/health`。dev-standardのoperation inventoryには業務外のplatform routeとして宣言し、lazunexと同じくIF帳票だけを持つ | 準拠 |

## 2. API契約

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| S20 | JSON命名 | `ApiBaseModel`でcamelCase alias | snake_case | camelCase（`resourceId`・`startAt`等） | 準拠 |
| S21 | エラー本文 | `{error:{code,message,details[{reason,statusCode,retryable,reference,resource}],traceId}}` | `{code, request_id}` | lazunex形式。業務理由は`details[0].reason`、`traceId`は`X-Request-ID`と一致 | 準拠 |
| S22 | 一覧 | `{items, nextToken}`とkeyset継続token | 配列と`offset` | `{items, nextToken}`へ変更。画面は継続tokenを積んで前ページへ戻る | 準拠 |
| S23 | path parameter | `{projectId}`等camelCase | `{resource_id}` | `{resourceId}`・`{reservationId}` | 準拠 |
| S24 | 標本 | `samples.py`の`status_samples`で全statusの要求・応答例 | なし | 全operationに追加し、OpenAPIとIF帳票へ反映 | 準拠 |
| S25 | 契約metadata | `contract.py`の`ApiContract`（auth_mode・permissions） | なし | 追加。auth_modeは`bearer-jwt` | 準拠（auth_mode値はS12） |
| S26 | 共通エラーstatus | 401/422/429/500 | 401/403/404/409/422/503 | lazunexの共通statusに503を追加（OCC再試行の上限超過） | 拡張（COM-06） |

## 3. 運用ログと例外

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| S30 | 運用ログ | `OperationalLogger`、operationごとのmessage catalog（`M00n`）、context schema | 1要求1行のJSON（`request_id`等） | lazunex形式。`http.request_completed`（`H001`）と各APIのcatalogを出力 | 準拠 |
| S31 | Router例外 | `ROUTER_HANDLED_EXCEPTIONS`を捕捉し`build_router_error_response`で応答と運用ログ | `DomainError`のexception handler | lazunex形式 | 準拠 |
| S32 | 例外型 | `ApiFunctionError`、`ExternalApiError`階層 | `DomainError` | lazunex形式（`common_errors.py`はbotocore非依存へ縮小） | 準拠 |

## 4. 設計文書

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| D01 | 配置 | `docs/spec/10.architecture`（手動）、`20.db`、`30.crud`、`40.apis`、`50.e2e`、`tools` | `docs/design/generated`へ単一生成器が一括出力 | lazunexの配置へ変更 | 準拠 |
| D02 | 生成物の命名 | `*_gen.md`・`*.gen.md`・`*.gen.csv`、手動は`*.manual.md` | 接尾辞なし | lazunexの命名へ変更 | 準拠 |
| D03 | API帳票 | `detail-design_gen.md`・`if_gen.md`・`messages_gen.md`・`query_gen.md`・`sequence_gen.md`・`unit-test_gen.md` | 6帳票を独自書式で生成 | lazunex生成器で生成。IF帳票だけdev-standardの固定kind名に合わせ`interface_gen.md` | 準拠（file名1件だけ差異） |
| D04 | API一覧・message索引 | `apis_list_gen.md`・`messages_index_gen.md` | なし | 追加 | 準拠 |
| D05 | DB文書 | `er.gen.md`（Mermaid ER図）と`tables/<table>.gen.md` | `DATA.md` | lazunex形式。論理FKは「論理FK -> 表(列)」と表記 | 準拠（表記はDSQL制約で拡張） |
| D06 | tools文書 | `docs/spec/tools/<tool>/basic-design_gen.md`・`unit-test-spec_gen.md`等 | なし | 追加 | 準拠 |
| D07 | architecture | `architecture.manual.md`、`sequence/`、`state/` | `docs/decisions`、`docs/OPERATIONS.md`、生成`OVERVIEW.md` | `10.architecture`へ移し、予約状態・予約作成シーケンス・判断記録・運用手順を配置 | 準拠 |
| D08 | 階層index | なし | 生成`index.md` | `40.apis`・group・APIごとに`index.md`を追加 | 拡張（dev-standard adapter契約） |
| D09 | 画面・infra・要件trace | なし | `FRONTEND.md`・`INFRA.md`・`TRACE.md`・`TESTS.md` | `60.frontend`・`70.infra`・`80.trace`へ移し、lazunexの番号体系に続けた | 拡張（TECH-DESIGN, TECH-PORTAL） |
| D10 | 詳細設計の見出し重複 | 同じ表・操作は1見出し | 該当なし | 同じ表への同じ操作が複数SQLにある場合だけ見出しにSQL名を付ける（`update_resource`） | 拡張（dev-standard profileの一意性） |
| D11 | 生成器の不具合 | 入れ子分岐のsequenceが平坦化され、単体テスト要因が入れ子を無視する | 該当なし | sequenceを木構造で描画し、入れ子if配下の要因を親要素が選ばれた組合せだけに展開 | 拡張（不具合修正） |

## 5. CRUD図の書き方

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| C01 | 形式 | API×テーブルの行列CSV（`db_crud.gen.csv`、セルは`CRUD`の組合せ） | operation×resourceの縦持ち表（`crud/matrix.md`）と図 | lazunexの行列CSVを正とする | 準拠 |
| C02 | 外部サービス | サービスごとの`<service>_crud.gen.csv`（API Gateway・Cognito・Secrets Manager） | なし | `identity_crud.gen.csv`（JWKS署名鍵の参照）。router依存`Depends(get_caller_identity)`も反映 | 準拠（対象サービスはS12・S13） |
| C03 | dev-standard射影 | なし | `crud/`に独自形式 | `30.crud/dev-standard/`に共通検査器と同じ射影（model・CSV・表・図・根拠）を生成 | 拡張（dev-standard adapter契約） |

## 6. E2E仕様

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| E01 | 仕様の持ち方 | `docs/spec/50.e2e/<flow>/`のcomponent/target/step/template/rules YAMLからケース一覧・シナリオを生成 | Playwrightのテストだけ | `reservation_lifecycle`フロー（6 component、22ケース）を追加 | 準拠 |
| E02 | 生成器の対象固定 | Project/APIの対象軸、既定前提variant、失敗の起こし方をPythonに直書き | 該当なし | 対象軸・依存・matrix期待・失敗手順を`flow.manual.yaml`とbinding YAMLへ移し、生成器を汎用化 | 拡張 |
| E03 | template検査 | 存在と構文だけ | 該当なし | step templateのmethod/path/operationIdとsample参照の実在も検査 | 拡張 |
| E04 | 実行型E2E | なし | Playwright（画面・ポータル） | 維持。E2E仕様は文書として並存 | 維持（COM-01, TECH-PORTAL） |

## 7. テスト構成

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| T01 | 配置 | `tests/app/apis/<group>/<operation>/test_router.py`・`test_functions.py`、`tests/tools`、`tests/integrations` | `backend/tests/test_*.py`、`infra/tests`、`tools/tests` | lazunexの配置へ移し、`tests/infra`を追加 | 準拠 |
| T02 | router試験 | 標本要求から期待応答を組み立て、DB状態を検査し、unit-test帳票の`TCnnn`をそのまま試験する | シナリオ単位の試験 | 全operationに標本・DB状態・`TCnnn`の試験を追加 | 準拠 |
| T03 | tools試験 | 37 moduleの生成器・検査器試験 | なし | 移植し、PostgreSQL・JWT・identityの差分だけ期待値を変更 | 準拠 |
| T04 | 受入条件タグ | なし | テスト説明に`[ID-AC]` | 維持し、要件traceを新配置へ更新 | 維持（TECH-DESIGN, TECH-QUALITY） |

## 8. 規約と検査

| ID | 項目 | lazunex | 変更前のSlotKeeper | 変更後 | 処置 |
|---|---|---|---|---|---|
| R01 | コーディング規約 | `docs/rule/coding/*.md`とrulecheck | なし | 移植し、管理対象literal・provider規約・PostgreSQLへ適応 | 準拠 |
| R02 | 文書語彙 | `docs/rule/docs/sequence_function_*.json` | なし | SlotKeeperの語彙で追加 | 準拠 |
| R03 | MUST規約の扱い | 検査のみ（lazunex自身も多数の違反を持つ） | 該当なし | `config/rulecheck_baseline.json`で継承負債を固定し、新規違反と解消済み項目の残存を失敗にする | 拡張 |
| R04 | router指標 | 分岐数・try本体の文数の閾値 | 該当なし | `create_reservation`・`cancel_reservation`・`update_resource`のrouterは処理順をrouterが所有する規約（S04）と閾値が衝突するためbaselineに残す | 維持（規約間の衝突） |
| R05 | 管理対象literal | `hub-admin`等 | 該当なし | `admin`・`confirmed`・`cancelled`・`created`・`room`・`equipment`。`contract.py`の`permissions`は静的検査のためliteralを許可 | 準拠 |

## 9. dev-standardとの接続

| ID | 項目 | 内容 | 処置 |
|---|---|---|---|
| A01 | 設計adapter | `src/tools/project/design.py`がlazunex生成器を`src/`の一時コピーで実行し、7能力（data・crud・api・tools・frontend・infra・trace）の所有rootへ出力する | 拡張 |
| A02 | API帳票profile | `.dev-standard/api-document-profile.json`（lazunexの見出しと`{group}/{api}/{kind}_gen.md`） | 拡張 |
| A03 | 参照tools棚卸し | `.dev-standard/reference-adoption.json`をlazunex 52 filesのtarget-adoptionへ更新（adopt 23・adapt 14・extend 15）。一覧は`docs/reference-tools.md` | 準拠 |

## 10. 検証状況

- 全pytest（498件、実PostgreSQL）、ruff、pyright、mypy、`app-codegen all --check`、`app-docs generate --check`、`app-archlint all`、rulecheck（checklist・baseline）、`design.py --manifest --check`、dev-standardの`check_design.py`（二重クリーン生成のbyte一致）、Quint check、画面のastro check・eslint・prettier・vitest・build、ポータルbuildとポータルE2Eを実行して成功した。
- Compose上のKeycloakと実APIを使う画面E2E（`e2e/app.spec.ts`）と性能測定は、この作業環境にDockerがないため実行していない。CIの`verify`で実行される。

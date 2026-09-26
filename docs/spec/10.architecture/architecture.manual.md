# SlotKeeper architecture

## 全体構成

静的Astro → HTTP API → FastAPI / Mangum（Lambda）→ Aurora DSQL。ローカルはPostgreSQL Repeatable ReadとKeycloakで同じ不変条件を検証する。

| 層 | 配置 | 責務 |
|---|---|---|
| 画面 | `frontend/` | Astro静的ページとReact island。OIDC PKCEでaccess tokenを取得し、生成したOpenAPI型でAPIを呼ぶ。 |
| API入口 | `src/app/main.py`, `src/app/lambda_handler.py` | FastAPIのapp生成、要求ID・運用ログmiddleware、共通エラー応答、Mangum adapter。 |
| API operation | `src/app/apis/<group>/<operation>/` | lazunex形式の1 operation 1所有単位。`router.py`が処理順・分岐・例外・transaction境界を所有し、`functions.py`が個別処理、`schemas.py`/`samples.py`/`contract.py`が公開契約、`sql/`と`generated/queries.py`がDBアクセスを持つ。 |
| 共通 | `src/app/apis/*.py`, `src/app/core/`, `src/app/db/` | 応答schema、エラーコード、運用ログcatalog、SQL実行、DSQL/PostgreSQL接続とOCC再試行。 |
| 外部連携 | `src/app/integrations/identity/` | JWT検証のport、JWKS provider、テスト用fake。業務層へ通信層固有の例外を漏らさない。 |
| DB | `src/db/ddl.sql` | `slotkeeper` schemaの正本DDL。DSQLに物理FKがないため論理FKを`-- REFERENCES`で記述する。 |
| 開発tool | `src/tools/`, `src/app_tool/` | lazunex由来の生成器・検査器と`app-docs`/`app-codegen`/`app-archlint`。 |
| インフラ | `infra/` | Python CDK。常設サーバーを持たない構成を合成する。 |

## 設計文書の配置

| 配置 | 内容 | 生成 |
|---|---|---|
| `docs/spec/10.architecture/` | 本書、判断記録、状態・シーケンス、運用手順 | 手動（`*.manual.md`） |
| `docs/spec/20.db/` | ER図、テーブル定義 | `generate_db_er_diagram`, `generate_db_table_specs` |
| `docs/spec/30.crud/` | API×DB/identityのCRUD表、dev-standard CRUD射影 | `generate_db_crud`, `generate_external_crud`, `design.py` |
| `docs/spec/40.apis/` | API一覧、6帳票（detail-design/interface/messages/query/sequence/unit-test）、OpenAPI | lazunex生成器 + `design.py` |
| `docs/spec/50.e2e/` | E2E仕様YAMLと生成ケース・シナリオ | `generate_e2e_case_list`, `generate_e2e_scenarios` |
| `docs/spec/60.frontend/` | 画面・状態・呼出API | `design.py` |
| `docs/spec/70.infra/` | CDK合成テンプレートと資源一覧 | `design.py` |
| `docs/spec/80.trace/` | 要件→受入条件→実在テストの追跡、テスト設計 | `design.py` |
| `docs/spec/tools/` | 生成器・検査器の基本設計と単体テスト仕様 | `app-docs generate-tools` |
| `docs/rule/` | コーディング規約、rulecheck checklist、文書語彙 | 手動・`rulecheck` |

生成物（`*.gen.md`, `*_gen.md`, `*.gen.csv`）は直接編集しない。

## 関連文書

- [予約状態](state/reservation_state.manual.md)
- [予約作成シーケンス](sequence/reservation_booking_sequence.manual.md)
- [運用手順](operations.manual.md)
- [判断記録: 初回構成](decisions/001-architecture.manual.md)
- [判断記録: 検証経路と要件trace](decisions/002-verification-and-trace.manual.md)
- [判断記録: lazunex構成への準拠](decisions/003-lazunex-alignment.manual.md)
- [lazunexとの差異一覧](lazunex-alignment.manual.md)

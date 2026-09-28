<!-- tools/quintflow.pyによる自動生成。spec/requirements/requirements.qntを編集すること。 -->
# SlotKeeper 要件一覧

- スキーマ版: 1
- カタログ版: 2
- Product(JSON): <code>"SlotKeeper"</code>
- 更新日(JSON): <code>"2026-09-26"</code>
- 正本: `spec/requirements/requirements.qnt`
- 機械可読view: `spec/requirements/requirements.json`

| ID | 版 | 状態 | 種別 | 原子的な義務 | 検証方法 |
|---|---:|---|---|---|---|
| <code>"COM-01"</code> | 2 | 有効 | 機能 | SlotKeeperは、幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さないを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-02"</code> | 2 | 有効 | 機能 | SlotKeeperは、確定済みのデータは再起動後も残る。失敗操作で部分更新を残さないを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-03"</code> | 2 | 有効 | 機能 | SlotKeeperは、入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別するを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-04"</code> | 2 | 有効 | 機能 | SlotKeeperは、サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らないを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-05"</code> | 2 | 有効 | 機能 | SlotKeeperは、起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できるを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-06"</code> | 2 | 有効 | 機能 | SlotKeeperは、資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内するを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-07"</code> | 2 | 有効 | 機能 | SlotKeeperは、要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しないを**提供する**（<code>"provide"</code>） | test |
| <code>"COM-08"</code> | 2 | 有効 | 機能 | SlotKeeperは、空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-01"</code> | 2 | 有効 | 機能 | SlotKeeperは、管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止するを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-02"</code> | 2 | 有効 | 機能 | SlotKeeperは、資源と日付を指定して、その日の予約済み時間帯を確認できるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-03"</code> | 2 | 有効 | 機能 | SlotKeeperは、資源、開始・終了、目的を指定して、自分名義の予約を作成できるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-04"</code> | 2 | 有効 | 機能 | SlotKeeperは、同一資源の予約済み時間と重なる予約の確定を拒否するを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-05"</code> | 2 | 有効 | 機能 | SlotKeeperは、本人または管理者が、開始前の予約を取消できるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-06"</code> | 2 | 有効 | 機能 | SlotKeeperは、自分の予約を日付・状態で絞り込めるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-07"</code> | 2 | 有効 | 機能 | SlotKeeperは、作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できるを**提供する**（<code>"provide"</code>） | test |
| <code>"SLOT-08"</code> | 2 | 有効 | 機能 | SlotKeeperは、要求の再送を識別し、予約と履歴を二重に作らないを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-STACK"</code> | 2 | 有効 | 制約 | SlotKeeperは、Astro静的フロントとFastAPIを使用するを**提供する**（<code>"provide"</code>） | check |
| <code>"TECH-DB"</code> | 2 | 有効 | 制約 | SlotKeeperは、DSQLとPostgreSQLで共通の予約不変条件を守るを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-AUTH"</code> | 2 | 有効 | 制約 | SlotKeeperは、署名、issuer、client、用途、期限を検査するを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-LAMBDA"</code> | 2 | 有効 | 制約 | SlotKeeperは、依存を含むLinux用Lambda ZIPを作成するを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-INFRA"</code> | 2 | 有効 | 制約 | SlotKeeperは、Python CDKで常設サーバーを持たない構成を合成するを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-COMPOSE"</code> | 2 | 有効 | 制約 | SlotKeeperは、GitとDocker Composeだけで起動と全検証を行えるを**提供する**（<code>"provide"</code>） | check |
| <code>"TECH-DESIGN"</code> | 2 | 有効 | 制約 | SlotKeeperは、実装から6帳票、DB、CRUD、画面、infraを決定的に生成するを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-PORTAL"</code> | 2 | 有効 | 制約 | SlotKeeperは、同一revisionとrunの実測結果と設計をPagesへ集約するを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-PERF"</code> | 2 | 有効 | 制約 | SlotKeeperは、指定負荷とデータ量でAPI別の性能を測定するを**提供する**（<code>"provide"</code>） | check |
| <code>"TECH-QUALITY"</code> | 2 | 有効 | 制約 | SlotKeeperは、型、lint、実DB、ブラウザ、負例検査の失敗を隠さないを**提供する**（<code>"provide"</code>） | test |
| <code>"TECH-PRIVACY"</code> | 2 | 有効 | 制約 | SlotKeeperは、公開allowlistに秘密や生ログを含めないを**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-01"</code> | 2 | 有効 | 制約 | SlotKeeperは、予約区間は &#96;[開始, 終了)&#96; とします。10:00〜11:00と11:00〜12:00は重複しません。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-02"</code> | 2 | 有効 | 制約 | SlotKeeperは、開始・終了は15分刻み、予約時間は15分以上4時間以下です。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-03"</code> | 2 | 有効 | 制約 | SlotKeeperは、開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-04"</code> | 2 | 有効 | 制約 | SlotKeeperは、保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-05"</code> | 2 | 有効 | 制約 | SlotKeeperは、予約状態は &#96;confirmed → cancelled&#96; です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-06"</code> | 2 | 有効 | 制約 | SlotKeeperは、取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-07"</code> | 2 | 有効 | 制約 | SlotKeeperは、既定の「将来予約」は &#96;confirmed AND start_at &gt; now&#96; とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-08"</code> | 2 | 有効 | 制約 | SlotKeeperは、将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-09"</code> | 2 | 有効 | 制約 | SlotKeeperは、一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-10"</code> | 2 | 有効 | 制約 | SlotKeeperは、予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-11"</code> | 2 | 有効 | 制約 | SlotKeeperは、成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-12"</code> | 2 | 有効 | 制約 | SlotKeeperは、予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-13"</code> | 2 | 有効 | 制約 | SlotKeeperは、取消済み予約への取消は409とします。履歴を追加しません。を**提供する**（<code>"provide"</code>） | test |
| <code>"RULE-14"</code> | 2 | 有効 | 制約 | SlotKeeperは、資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。を**提供する**（<code>"provide"</code>） | test |

## COM-01: 幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない

要件ID(JSON): <code>"COM-01"</code>
タイトル(JSON): <code>"幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない"</code>
SlotKeeperは、幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-01-AC"</code> 前提: 一般利用者が390pxと1280pxの画面でログインしている。条件: 資源選択・予約作成・詳細・取消・ログアウトをキーボード操作可能な部品で行う。期待結果: 各操作が完了し、ページ全体の横スクロール幅が表示幅以下で、localStorageにtokenを残さない。
  - criterion(JSON Object): <code>{"given":"一般利用者が390pxと1280pxの画面でログインしている","id":"COM-01-AC","then":"各操作が完了し、ページ全体の横スクロール幅が表示幅以下で、localStorageにtokenを残さない","when":"資源選択・予約作成・詳細・取消・ログアウトをキーボード操作可能な部品で行う"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/60.frontend/frontend.gen.md"]</code>
- 実装: <code>["frontend/src/App.tsx","frontend/src/style.css","frontend/src/logic.ts"]</code>
- テスト: <code>["e2e/app.spec.ts","frontend/tests/logic.test.ts"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-02: 確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない

要件ID(JSON): <code>"COM-02"</code>
タイトル(JSON): <code>"確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない"</code>
SlotKeeperは、確定済みのデータは再起動後も残る。失敗操作で部分更新を残さないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-02-AC"</code> 前提: 確定済み予約と途中で失敗する作成要求がある。条件: migration・seedの再実行と履歴保存中の障害を起こす。期待結果: 確定データは保持され、失敗した要求は予約・履歴・要求キーを残さない。
  - criterion(JSON Object): <code>{"given":"確定済み予約と途中で失敗する作成要求がある","id":"COM-02-AC","then":"確定データは保持され、失敗した要求は予約・履歴・要求キーを残さない","when":"migration・seedの再実行と履歴保存中の障害を起こす"}</code>
- <code>"SLOT-AC16"</code> 前提: 確定データと開発用seedがある。条件: 起動・seed・アプリ再起動を繰り返す。期待結果: 確定データを保持し、seedの無条件重複や開発データ消去を起こさない。
  - criterion(JSON Object): <code>{"given":"確定データと開発用seedがある","id":"SLOT-AC16","then":"確定データを保持し、seedの無条件重複や開発データ消去を起こさない","when":"起動・seed・アプリ再起動を繰り返す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/20.db/er.gen.md"]</code>
- 実装: <code>["src/app/db/session.py","src/tools/project/migrate.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_router.py","tests/test_db_session.py","tests/tools/test_project_migrate.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-03: 入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する

要件ID(JSON): <code>"COM-03"</code>
タイトル(JSON): <code>"入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する"</code>
SlotKeeperは、入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-03-AC"</code> 前提: 不正入力・未認証・権限不足・存在しない対象・業務競合の要求がある。条件: 各APIを呼び出す。期待結果: それぞれ422・401・403・404・409を返し、入力値を応答へ反射しない。
  - criterion(JSON Object): <code>{"given":"不正入力・未認証・権限不足・存在しない対象・業務競合の要求がある","id":"COM-03-AC","then":"それぞれ422・401・403・404・409を返し、入力値を応答へ反射しない","when":"各APIを呼び出す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/main.py","src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py","tests/app/apis/reservations/get_reservation/test_router.py","tests/app/apis/reservations/list_reservations/test_functions.py","tests/app/apis/resources/create_resource/test_functions.py","tests/app/apis/resources/get_resource_schedule/test_functions.py","tests/app/apis/resources/get_resource_schedule/test_router.py","tests/app/apis/resources/list_resources/test_functions.py","tests/app/apis/resources/update_resource/test_router.py","tests/app/apis/test_deps.py","tests/test_api_error_responses.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-04: サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない

要件ID(JSON): <code>"COM-04"</code>
タイトル(JSON): <code>"サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない"</code>
SlotKeeperは、サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-04-AC"</code> 前提: 一般利用者のtokenと任意の権限ヘッダーがある。条件: 管理API・他人の予約の詳細と取消を呼び出す。期待結果: サーバー側で403とし、UI表示に依存せず拒否する。
  - criterion(JSON Object): <code>{"given":"一般利用者のtokenと任意の権限ヘッダーがある","id":"COM-04-AC","then":"サーバー側で403とし、UI表示に依存せず拒否する","when":"管理API・他人の予約の詳細と取消を呼び出す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/deps.py","src/app/integrations/identity/jwt_provider/client.py","src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py"]</code>
- テスト: <code>["e2e/app.spec.ts","tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/get_reservation/test_functions.py","tests/app/apis/reservations/get_reservation/test_router.py","tests/app/apis/resources/create_resource/test_functions.py","tests/app/apis/resources/create_resource/test_router.py","tests/app/apis/resources/update_resource/test_router.py","tests/app/apis/test_deps.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-05: 起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる

要件ID(JSON): <code>"COM-05"</code>
タイトル(JSON): <code>"起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる"</code>
SlotKeeperは、起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-05-AC"</code> 前提: Git checkoutとDocker Composeだけがある。条件: 起動・seed・全検証のCompose commandを繰り返す。期待結果: 依存の準備から検証まで完了し、seedは固定IDで重複しない。
  - criterion(JSON Object): <code>{"given":"Git checkoutとDocker Composeだけがある","id":"COM-05-AC","then":"依存の準備から検証まで完了し、seedは固定IDで重複しない","when":"起動・seed・全検証のCompose commandを繰り返す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/operations.manual.md"]</code>
- 実装: <code>["compose.yaml","src/tools/project/migrate.py","src/tools/project/verify.py"]</code>
- テスト: <code>["tests/tools/test_project_migrate.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-06: 資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する

要件ID(JSON): <code>"COM-06"</code>
タイトル(JSON): <code>"資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する"</code>
SlotKeeperは、資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC11"</code> 前提: 資源または予約が他の操作で先に更新されている。条件: 古い版で資源編集・予約取消を送る。期待結果: 409を返し、先に確定した値と履歴を失わない。
  - criterion(JSON Object): <code>{"given":"資源または予約が他の操作で先に更新されている","id":"SLOT-AC11","then":"409を返し、先に確定した値と履歴を失わない","when":"古い版で資源編集・予約取消を送る"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/resources/update_resource/index.md","docs/spec/40.apis/reservations/cancel_reservation/index.md"]</code>
- 実装: <code>["src/app/apis/resources/update_resource/router.py","src/app/apis/resources/update_resource/functions.py","src/app/apis/reservations/cancel_reservation/router.py","src/app/apis/reservations/cancel_reservation/functions.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_functions.py","tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/resources/update_resource/test_functions.py","tests/app/apis/resources/update_resource/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-07: 要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない

要件ID(JSON): <code>"COM-07"</code>
タイトル(JSON): <code>"要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない"</code>
SlotKeeperは、要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-07-AC"</code> 前提: 予約目的とBearer tokenを含む要求がある。条件: APIを呼び出す。期待結果: 要求ID・operation・status・所要時間を構造化ログに残し、目的とtokenを記録しない。
  - criterion(JSON Object): <code>{"given":"予約目的とBearer tokenを含む要求がある","id":"COM-07-AC","then":"要求ID・operation・status・所要時間を構造化ログに残し、目的とtokenを記録しない","when":"APIを呼び出す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/create_reservation/messages_gen.md"]</code>
- 実装: <code>["src/app/main.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/create_reservation/test_router.py","tests/app/apis/reservations/get_reservation/test_router.py","tests/app/apis/reservations/list_reservations/test_router.py","tests/app/apis/resources/create_resource/test_router.py","tests/app/apis/resources/get_resource_schedule/test_router.py","tests/app/apis/resources/list_resources/test_router.py","tests/app/apis/resources/update_resource/test_router.py","tests/test_operational_logging.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## COM-08: 空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる

要件ID(JSON): <code>"COM-08"</code>
タイトル(JSON): <code>"空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる"</code>
SlotKeeperは、空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-08-AC"</code> 前提: 通信失敗・401・403・404・409・422・503と業務コードがある。条件: 画面の案内文を求める。期待結果: 状態ごとに異なり次の操作を判断できる日本語の案内を返す。
  - criterion(JSON Object): <code>{"given":"通信失敗・401・403・404・409・422・503と業務コードがある","id":"COM-08-AC","then":"状態ごとに異なり次の操作を判断できる日本語の案内を返す","when":"画面の案内文を求める"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/60.frontend/frontend.gen.md"]</code>
- 実装: <code>["frontend/src/logic.ts","frontend/src/App.tsx"]</code>
- テスト: <code>["frontend/tests/logic.test.ts"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-01: 管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する

要件ID(JSON): <code>"SLOT-01"</code>
タイトル(JSON): <code>"管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する"</code>
SlotKeeperは、管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-01-AC"</code> 前提: 管理者と一般利用者がいる。条件: 資源の登録・編集・無効化と一覧取得を行う。期待結果: 管理者だけが変更でき、一覧は名前とIDの固定順でページングされる。
  - criterion(JSON Object): <code>{"given":"管理者と一般利用者がいる","id":"SLOT-01-AC","then":"管理者だけが変更でき、一覧は名前とIDの固定順でページングされる","when":"資源の登録・編集・無効化と一覧取得を行う"}</code>
- <code>"SLOT-AC05"</code> 前提: 無効資源と将来予約のある有効資源がある。条件: 無効資源への予約と、将来予約のある資源の無効化を行う。期待結果: 両方409で拒否し、データは変化しない。
  - criterion(JSON Object): <code>{"given":"無効資源と将来予約のある有効資源がある","id":"SLOT-AC05","then":"両方409で拒否し、データは変化しない","when":"無効資源への予約と、将来予約のある資源の無効化を行う"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/resources/index.md"]</code>
- 実装: <code>["src/app/apis/resources/create_resource/router.py","src/app/apis/resources/create_resource/functions.py","src/app/apis/resources/update_resource/router.py","src/app/apis/resources/update_resource/functions.py","src/app/apis/resources/list_resources/router.py","src/app/apis/resources/list_resources/functions.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py","tests/app/apis/resources/create_resource/test_functions.py","tests/app/apis/resources/create_resource/test_router.py","tests/app/apis/resources/list_resources/test_functions.py","tests/app/apis/resources/list_resources/test_router.py","tests/app/apis/resources/update_resource/test_functions.py","tests/app/apis/resources/update_resource/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-02: 資源と日付を指定して、その日の予約済み時間帯を確認できる

要件ID(JSON): <code>"SLOT-02"</code>
タイトル(JSON): <code>"資源と日付を指定して、その日の予約済み時間帯を確認できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"資源と日付を指定して、その日の予約済み時間帯を確認できる"</code>
SlotKeeperは、資源と日付を指定して、その日の予約済み時間帯を確認できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-02-AC"</code> 前提: 資源に確定予約と取消済み予約がある。条件: 一般利用者が資源と日付で予約表を取得する。期待結果: 確定済みの時間帯と「予約済み」だけを返し、他人の目的と識別情報を返さない。
  - criterion(JSON Object): <code>{"given":"資源に確定予約と取消済み予約がある","id":"SLOT-02-AC","then":"確定済みの時間帯と「予約済み」だけを返し、他人の目的と識別情報を返さない","when":"一般利用者が資源と日付で予約表を取得する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/resources/get_resource_schedule/index.md"]</code>
- 実装: <code>["src/app/apis/resources/get_resource_schedule/router.py","src/app/apis/resources/get_resource_schedule/functions.py"]</code>
- テスト: <code>["e2e/app.spec.ts","tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/resources/get_resource_schedule/test_functions.py","tests/app/apis/resources/get_resource_schedule/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-03: 資源、開始・終了、目的を指定して、自分名義の予約を作成できる

要件ID(JSON): <code>"SLOT-03"</code>
タイトル(JSON): <code>"資源、開始・終了、目的を指定して、自分名義の予約を作成できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"資源、開始・終了、目的を指定して、自分名義の予約を作成できる"</code>
SlotKeeperは、資源、開始・終了、目的を指定して、自分名義の予約を作成できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC01"</code> 前提: 空き資源がある。条件: 翌日10:00〜11:00を予約する。期待結果: 1件確定し、予約表と自分の一覧へ反映する。
  - criterion(JSON Object): <code>{"given":"空き資源がある","id":"SLOT-AC01","then":"1件確定し、予約表と自分の一覧へ反映する","when":"翌日10:00〜11:00を予約する"}</code>
- <code>"SLOT-AC06"</code> 前提: 過去・現在と同時刻・0分・4時間超・30日超・15分未満の刻み・日跨ぎの入力がある。条件: 予約時刻を検証する。期待結果: 入力エラーとし、15分・4時間・30日以内の境界は受け付ける。
  - criterion(JSON Object): <code>{"given":"過去・現在と同時刻・0分・4時間超・30日超・15分未満の刻み・日跨ぎの入力がある","id":"SLOT-AC06","then":"入力エラーとし、15分・4時間・30日以内の境界は受け付ける","when":"予約時刻を検証する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/create_reservation/index.md"]</code>
- 実装: <code>["src/app/apis/reservations/create_reservation/router.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/common.py"]</code>
- テスト: <code>["e2e/app.spec.ts","tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-04: 同一資源の予約済み時間と重なる予約の確定を拒否する

要件ID(JSON): <code>"SLOT-04"</code>
タイトル(JSON): <code>"同一資源の予約済み時間と重なる予約の確定を拒否する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"同一資源の予約済み時間と重なる予約の確定を拒否する"</code>
SlotKeeperは、同一資源の予約済み時間と重なる予約の確定を拒否するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC02"</code> 前提: 既存の10:00〜11:00予約がある。条件: 10:30〜11:30と11:00〜12:00を予約する。期待結果: 前者409、後者成功。
  - criterion(JSON Object): <code>{"given":"既存の10:00〜11:00予約がある","id":"SLOT-AC02","then":"前者409、後者成功","when":"10:30〜11:30と11:00〜12:00を予約する"}</code>
- <code>"SLOT-AC03"</code> 前提: 空き枠に20人がいる。条件: 直列化せず同時に予約する。期待結果: 1件成功・19件409で重複0件。
  - criterion(JSON Object): <code>{"given":"空き枠に20人がいる","id":"SLOT-AC03","then":"1件成功・19件409で重複0件","when":"直列化せず同時に予約する"}</code>
- <code>"SLOT-AC10"</code> 前提: 有効資源がある。条件: 予約作成と資源無効化を同時実行する。期待結果: 無効化と将来予約が両方確定する結果は0件。
  - criterion(JSON Object): <code>{"given":"有効資源がある","id":"SLOT-AC10","then":"無効化と将来予約が両方確定する結果は0件","when":"予約作成と資源無効化を同時実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/create_reservation/sequence_gen.md","docs/spec/20.db/er.gen.md"]</code>
- 実装: <code>["src/app/apis/reservations/create_reservation/router.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/sql/002_update_resources_control_version.sql","src/app/db/session.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py","tests/app/apis/resources/update_resource/test_router.py","tests/test_db_session.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-05: 本人または管理者が、開始前の予約を取消できる

要件ID(JSON): <code>"SLOT-05"</code>
タイトル(JSON): <code>"本人または管理者が、開始前の予約を取消できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"本人または管理者が、開始前の予約を取消できる"</code>
SlotKeeperは、本人または管理者が、開始前の予約を取消できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC04"</code> 前提: 利用者Aの開始前予約がある。条件: B・A・管理者が取消を試みる。期待結果: Bは403、本人と管理者は取消でき、取消履歴が追加される。
  - criterion(JSON Object): <code>{"given":"利用者Aの開始前予約がある","id":"SLOT-AC04","then":"Bは403、本人と管理者は取消でき、取消履歴が追加される","when":"B・A・管理者が取消を試みる"}</code>
- <code>"SLOT-AC13"</code> 前提: 開始時刻ちょうどの予約と取消済み予約がある。条件: 取消する。期待結果: 409で拒否し、履歴を増やさない。
  - criterion(JSON Object): <code>{"given":"開始時刻ちょうどの予約と取消済み予約がある","id":"SLOT-AC13","then":"409で拒否し、履歴を増やさない","when":"取消する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/cancel_reservation/index.md"]</code>
- 実装: <code>["src/app/apis/reservations/cancel_reservation/router.py","src/app/apis/reservations/cancel_reservation/functions.py"]</code>
- テスト: <code>["e2e/app.spec.ts","tests/app/apis/reservations/cancel_reservation/test_functions.py","tests/app/apis/reservations/cancel_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-06: 自分の予約を日付・状態で絞り込める

要件ID(JSON): <code>"SLOT-06"</code>
タイトル(JSON): <code>"自分の予約を日付・状態で絞り込める"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"自分の予約を日付・状態で絞り込める"</code>
SlotKeeperは、自分の予約を日付・状態で絞り込めるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC08"</code> 前提: 自分と他人の予約が複数日・複数状態にある。条件: 日付・状態で絞込み、他人の詳細を取得する。期待結果: 自分の対象だけを返し、他人の目的・履歴は403で漏れない。
  - criterion(JSON Object): <code>{"given":"自分と他人の予約が複数日・複数状態にある","id":"SLOT-AC08","then":"自分の対象だけを返し、他人の目的・履歴は403で漏れない","when":"日付・状態で絞込み、他人の詳細を取得する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/list_reservations/index.md"]</code>
- 実装: <code>["src/app/apis/reservations/list_reservations/router.py","src/app/apis/reservations/list_reservations/functions.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/list_reservations/test_functions.py","tests/app/apis/reservations/list_reservations/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-07: 作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる

要件ID(JSON): <code>"SLOT-07"</code>
タイトル(JSON): <code>"作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる"</code>
SlotKeeperは、作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-07-AC"</code> 前提: 作成後に取消した予約がある。条件: 本人・管理者・他人が詳細画面で履歴を取得する。期待結果: 本人と管理者は作成・取消の順の履歴を閲覧でき、他人は403。
  - criterion(JSON Object): <code>{"given":"作成後に取消した予約がある","id":"SLOT-07-AC","then":"本人と管理者は作成・取消の順の履歴を閲覧でき、他人は403","when":"本人・管理者・他人が詳細画面で履歴を取得する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/get_reservation/index.md"]</code>
- 実装: <code>["src/app/apis/reservations/get_reservation/router.py","src/app/apis/reservations/get_reservation/functions.py"]</code>
- テスト: <code>["e2e/app.spec.ts","tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/get_reservation/test_functions.py","tests/app/apis/reservations/get_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## SLOT-08: 要求の再送を識別し、予約と履歴を二重に作らない

要件ID(JSON): <code>"SLOT-08"</code>
タイトル(JSON): <code>"要求の再送を識別し、予約と履歴を二重に作らない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"要求の再送を識別し、予約と履歴を二重に作らない"</code>
SlotKeeperは、要求の再送を識別し、予約と履歴を二重に作らないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `functional`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-AC07"</code> 前提: 成功応答を失った作成要求がある。条件: 同じキーで再送（同時再送を含む）する。期待結果: 元の予約IDと応答を返し、予約・作成履歴は各1件。
  - criterion(JSON Object): <code>{"given":"成功応答を失った作成要求がある","id":"SLOT-AC07","then":"元の予約IDと応答を返し、予約・作成履歴は各1件","when":"同じキーで再送（同時再送を含む）する"}</code>
- <code>"SLOT-AC09"</code> 前提: 同じ要求キーの成功記録がある。条件: 異なる入力を送る。期待結果: 409で元の予約を変更しない。
  - criterion(JSON Object): <code>{"given":"同じ要求キーの成功記録がある","id":"SLOT-AC09","then":"409で元の予約を変更しない","when":"異なる入力を送る"}</code>
- <code>"SLOT-AC12"</code> 前提: 予約保存後の履歴保存で障害が起きる。条件: 作成し、その後同じキーで再送する。期待結果: 部分保存を残さず、再送で1件だけ作成する。
  - criterion(JSON Object): <code>{"given":"予約保存後の履歴保存で障害が起きる","id":"SLOT-AC12","then":"部分保存を残さず、再送で1件だけ作成する","when":"作成し、その後同じキーで再送する"}</code>
- <code>"SLOT-AC15"</code> 前提: 作成済みキーの経過が24時間前後で、予約は取消・開始済みである。条件: 同じキーで再送する。期待結果: 有効期間内は元の作成結果、期限後は新規要求の規則に従う。
  - criterion(JSON Object): <code>{"given":"作成済みキーの経過が24時間前後で、予約は取消・開始済みである","id":"SLOT-AC15","then":"有効期間内は元の作成結果、期限後は新規要求の規則に従う","when":"同じキーで再送する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/reservations/create_reservation/sequence_gen.md"]</code>
- 実装: <code>["src/app/apis/reservations/create_reservation/router.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/sql/001_select_idempotency_records.sql","src/app/apis/reservations/create_reservation/sql/006_insert_reservations.sql"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py","tests/test_db_session.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-STACK: Astro静的フロントとFastAPIを使用する

要件ID(JSON): <code>"TECH-STACK"</code>
タイトル(JSON): <code>"Astro静的フロントとFastAPIを使用する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"Astro静的フロントとFastAPIを使用する"</code>
SlotKeeperは、Astro静的フロントとFastAPIを使用するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-STACK-AC"</code> 前提: Astro画面・FastAPI・PostgreSQLを起動している。条件: 静的buildとOpenAPI型生成を検査する。期待結果: 静的成果物がbuildでき、フロント型がOpenAPIとdriftしない。
  - criterion(JSON Object): <code>{"given":"Astro画面・FastAPI・PostgreSQLを起動している","id":"TECH-STACK-AC","then":"静的成果物がbuildでき、フロント型がOpenAPIとdriftしない","when":"静的buildとOpenAPI型生成を検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: check
検証証跡: verify:astro, verify:frontend-build, verify:openapi-types
検証(JSON Object): <code>{"evidence":"verify:astro, verify:frontend-build, verify:openapi-types","method":"check"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/architecture.manual.md"]</code>
- 実装: <code>["frontend/astro.config.mjs","src/app/main.py","src/tools/frontend.mjs"]</code>
- テスト: <code>[]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-DB: DSQLとPostgreSQLで共通の予約不変条件を守る

要件ID(JSON): <code>"TECH-DB"</code>
タイトル(JSON): <code>"DSQLとPostgreSQLで共通の予約不変条件を守る"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"DSQLとPostgreSQLで共通の予約不変条件を守る"</code>
SlotKeeperは、DSQLとPostgreSQLで共通の予約不変条件を守るを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-DB-AC"</code> 前提: ローカルPostgreSQLの検証DBがある。条件: 接続の分離レベルと共通SQLの型を検査する。期待結果: Repeatable Readで接続し、SQL正本の束縛引数と結果型が一致する。
  - criterion(JSON Object): <code>{"given":"ローカルPostgreSQLの検証DBがある","id":"TECH-DB-AC","then":"Repeatable Readで接続し、SQL正本の束縛引数と結果型が一致する","when":"接続の分離レベルと共通SQLの型を検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/20.db/er.gen.md"]</code>
- 実装: <code>["src/app/db/session.py","src/tools/generate_queries.py","src/tools/project/migrate.py"]</code>
- テスト: <code>["tests/test_db_session.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-AUTH: 署名、issuer、client、用途、期限を検査する

要件ID(JSON): <code>"TECH-AUTH"</code>
タイトル(JSON): <code>"署名、issuer、client、用途、期限を検査する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"署名、issuer、client、用途、期限を検査する"</code>
SlotKeeperは、署名、issuer、client、用途、期限を検査するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"SLOT-AC14"</code> 前提: 不正署名・期限切れ・異なるissuer/client・role改ざん・ID tokenがある。条件: 業務APIを呼び出す。期待結果: 401/403で拒否し、DBは変化しない。
  - criterion(JSON Object): <code>{"given":"不正署名・期限切れ・異なるissuer/client・role改ざん・ID tokenがある","id":"SLOT-AC14","then":"401/403で拒否し、DBは変化しない","when":"業務APIを呼び出す"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/deps.py","src/app/integrations/identity/jwt_provider/client.py","frontend/src/auth.ts"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_router.py","tests/app/apis/test_deps.py","tests/integrations/test_identity_provider.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-LAMBDA: 依存を含むLinux用Lambda ZIPを作成する

要件ID(JSON): <code>"TECH-LAMBDA"</code>
タイトル(JSON): <code>"依存を含むLinux用Lambda ZIPを作成する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"依存を含むLinux用Lambda ZIPを作成する"</code>
SlotKeeperは、依存を含むLinux用Lambda ZIPを作成するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-LAMBDA-AC"</code> 前提: Compose内でLinux向けに作った配布ZIPがある。条件: 隔離pathからimportし、API Gatewayイベントを変換する。期待結果: handlerを読み込み、healthは200・未認証の業務APIは401。
  - criterion(JSON Object): <code>{"given":"Compose内でLinux向けに作った配布ZIPがある","id":"TECH-LAMBDA-AC","then":"handlerを読み込み、healthは200・未認証の業務APIは401","when":"隔離pathからimportし、API Gatewayイベントを変換する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/70.infra/infra.gen.md"]</code>
- 実装: <code>["src/tools/project/package_lambda.py","src/app/main.py"]</code>
- テスト: <code>["tests/test_lambda_handler.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-INFRA: Python CDKで常設サーバーを持たない構成を合成する

要件ID(JSON): <code>"TECH-INFRA"</code>
タイトル(JSON): <code>"Python CDKで常設サーバーを持たない構成を合成する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"Python CDKで常設サーバーを持たない構成を合成する"</code>
SlotKeeperは、Python CDKで常設サーバーを持たない構成を合成するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-INFRA-AC"</code> 前提: AWS認証情報のない環境で環境contextを指定する。条件: CDKをsynthしassertionとcdk-nagで検査する。期待結果: 非公開S3+OAC、JWT保護route、限定IAM、ログ保持、削除保護、環境別のCORSとcallbackを満たし、常設サーバーを持たない。
  - criterion(JSON Object): <code>{"given":"AWS認証情報のない環境で環境contextを指定する","id":"TECH-INFRA-AC","then":"非公開S3+OAC、JWT保護route、限定IAM、ログ保持、削除保護、環境別のCORSとcallbackを満たし、常設サーバーを持たない","when":"CDKをsynthしassertionとcdk-nagで検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/70.infra/infra.gen.md"]</code>
- 実装: <code>["infra/stack.py","infra/app.py"]</code>
- テスト: <code>["tests/infra/test_stack.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-COMPOSE: GitとDocker Composeだけで起動と全検証を行える

要件ID(JSON): <code>"TECH-COMPOSE"</code>
タイトル(JSON): <code>"GitとDocker Composeだけで起動と全検証を行える"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"GitとDocker Composeだけで起動と全検証を行える"</code>
SlotKeeperは、GitとDocker Composeだけで起動と全検証を行えるを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-COMPOSE-AC"</code> 前提: ホストにGitとDocker Composeだけがある。条件: verifyを1コマンドで実行する。期待結果: 依存serviceの準備から結果収集とポータル生成まで行い、失敗時は非0で終了する。
  - criterion(JSON Object): <code>{"given":"ホストにGitとDocker Composeだけがある","id":"TECH-COMPOSE-AC","then":"依存serviceの準備から結果収集とポータル生成まで行い、失敗時は非0で終了する","when":"verifyを1コマンドで実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: check
検証証跡: verify:package, verify:backend, verify:e2e, verify:portal-build
検証(JSON Object): <code>{"evidence":"verify:package, verify:backend, verify:e2e, verify:portal-build","method":"check"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/operations.manual.md"]</code>
- 実装: <code>["compose.yaml","Dockerfile","src/tools/project/verify.py"]</code>
- テスト: <code>[]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-DESIGN: 実装から6帳票、DB、CRUD、画面、infraを決定的に生成する

要件ID(JSON): <code>"TECH-DESIGN"</code>
タイトル(JSON): <code>"実装から6帳票、DB、CRUD、画面、infraを決定的に生成する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"実装から6帳票、DB、CRUD、画面、infraを決定的に生成する"</code>
SlotKeeperは、実装から6帳票、DB、CRUD、画面、infraを決定的に生成するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-DESIGN-AC"</code> 前提: 実装source・SQL・CDKがある。条件: 設計を2回クリーン生成し、既存生成物と比較する。期待結果: byte一致し、欠落・変更・余剰・未対応構文・要件traceの欠落を非0で報告する。
  - criterion(JSON Object): <code>{"given":"実装source・SQL・CDKがある","id":"TECH-DESIGN-AC","then":"byte一致し、欠落・変更・余剰・未対応構文・要件traceの欠落を非0で報告する","when":"設計を2回クリーン生成し、既存生成物と比較する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/report.json"]</code>
- 実装: <code>["src/tools/project/design.py",".dev-standard/design.json"]</code>
- テスト: <code>["tests/tools/test_project_design.py","tests/tools/test_project_evidence.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-PORTAL: 同一revisionとrunの実測結果と設計をPagesへ集約する

要件ID(JSON): <code>"TECH-PORTAL"</code>
タイトル(JSON): <code>"同一revisionとrunの実測結果と設計をPagesへ集約する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"同一revisionとrunの実測結果と設計をPagesへ集約する"</code>
SlotKeeperは、同一revisionとrunの実測結果と設計をPagesへ集約するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PORTAL-AC"</code> 前提: 同一revision・runの検査結果と生成設計がある。条件: ポータルをbuildしブラウザで検証する。期待結果: 階層・検索・図の拡大・DB探索・深いリンク・390px表示が動作する。
  - criterion(JSON Object): <code>{"given":"同一revision・runの検査結果と生成設計がある","id":"TECH-PORTAL-AC","then":"階層・検索・図の拡大・DB探索・深いリンク・390px表示が動作する","when":"ポータルをbuildしブラウザで検証する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/architecture.manual.md"]</code>
- 実装: <code>["src/tools/project/evidence.py","portal/src/layouts/Layout.astro"]</code>
- テスト: <code>["e2e/portal.spec.ts"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-PERF: 指定負荷とデータ量でAPI別の性能を測定する

要件ID(JSON): <code>"TECH-PERF"</code>
タイトル(JSON): <code>"指定負荷とデータ量でAPI別の性能を測定する"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"指定負荷とデータ量でAPI別の性能を測定する"</code>
SlotKeeperは、指定負荷とデータ量でAPI別の性能を測定するを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PERF-AC"</code> 前提: 資源100・利用者200・予約10万件のデータがある。条件: 20並列で参照80%・作成取消20%の負荷を測定する。期待結果: API別のp50/p95/p99・throughput・エラー率・整合性違反を同一runの証跡に残す。
  - criterion(JSON Object): <code>{"given":"資源100・利用者200・予約10万件のデータがある","id":"TECH-PERF-AC","then":"API別のp50/p95/p99・throughput・エラー率・整合性違反を同一runの証跡に残す","when":"20並列で参照80%・作成取消20%の負荷を測定する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: check
検証証跡: verify:performance
検証(JSON Object): <code>{"evidence":"verify:performance","method":"check"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/architecture.manual.md"]</code>
- 実装: <code>["src/tools/project/perf.py"]</code>
- テスト: <code>[]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-QUALITY: 型、lint、実DB、ブラウザ、負例検査の失敗を隠さない

要件ID(JSON): <code>"TECH-QUALITY"</code>
タイトル(JSON): <code>"型、lint、実DB、ブラウザ、負例検査の失敗を隠さない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"型、lint、実DB、ブラウザ、負例検査の失敗を隠さない"</code>
SlotKeeperは、型、lint、実DB、ブラウザ、負例検査の失敗を隠さないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-QUALITY-AC"</code> 前提: 失敗・skip・未実行・flakyを含む結果がある。条件: 結果を共通形式へ変換する。期待結果: 非成功状態を成功へ変えず、collector外の結果と別runの混入を拒否する。
  - criterion(JSON Object): <code>{"given":"失敗・skip・未実行・flakyを含む結果がある","id":"TECH-QUALITY-AC","then":"非成功状態を成功へ変えず、collector外の結果と別runの混入を拒否する","when":"結果を共通形式へ変換する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/80.trace/tests.gen.md"]</code>
- 実装: <code>["src/tools/project/evidence.py","src/tools/project/collector.py","src/tools/project/verify.py"]</code>
- テスト: <code>["tests/tools/test_project_evidence.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## TECH-PRIVACY: 公開allowlistに秘密や生ログを含めない

要件ID(JSON): <code>"TECH-PRIVACY"</code>
タイトル(JSON): <code>"公開allowlistに秘密や生ログを含めない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"公開allowlistに秘密や生ログを含めない"</code>
SlotKeeperは、公開allowlistに秘密や生ログを含めないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PRIVACY-AC"</code> 前提: 公開サイトにallowlist外のfileやsymlinkがある。条件: 公開集合を検査する。期待結果: 公開を拒否し、生ログ・token・DB dumpを含めない。
  - criterion(JSON Object): <code>{"given":"公開サイトにallowlist外のfileやsymlinkがある","id":"TECH-PRIVACY-AC","then":"公開を拒否し、生ログ・token・DB dumpを含めない","when":"公開集合を検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/10.architecture/architecture.manual.md"]</code>
- 実装: <code>["src/tools/project/evidence.py"]</code>
- テスト: <code>["tests/tools/test_project_evidence.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-01: 予約区間は &#96;[開始, 終了)&#96; とします。10:00〜11:00と11:00〜12:00は重複しません。

要件ID(JSON): <code>"RULE-01"</code>
タイトル(JSON): <code>"予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。"</code>
SlotKeeperは、予約区間は &#96;[開始, 終了)&#96; とします。10:00〜11:00と11:00〜12:00は重複しません。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-01-AC"</code> 前提: 10:00〜11:00の予約がある。条件: 11:00〜12:00を予約する。期待結果: 半開区間として重複せず成功する。
  - criterion(JSON Object): <code>{"given":"10:00〜11:00の予約がある","id":"RULE-01-AC","then":"半開区間として重複せず成功する","when":"11:00〜12:00を予約する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-02: 開始・終了は15分刻み、予約時間は15分以上4時間以下です。

要件ID(JSON): <code>"RULE-02"</code>
タイトル(JSON): <code>"開始・終了は15分刻み、予約時間は15分以上4時間以下です。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"開始・終了は15分刻み、予約時間は15分以上4時間以下です。"</code>
SlotKeeperは、開始・終了は15分刻み、予約時間は15分以上4時間以下です。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-02-AC"</code> 前提: 15分刻みでない、15分未満、4時間超の入力がある。条件: 時刻を検証する。期待結果: 422とし、15分と4時間ちょうどは受け付ける。
  - criterion(JSON Object): <code>{"given":"15分刻みでない、15分未満、4時間超の入力がある","id":"RULE-02-AC","then":"422とし、15分と4時間ちょうどは受け付ける","when":"時刻を検証する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-03: 開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。

要件ID(JSON): <code>"RULE-03"</code>
タイトル(JSON): <code>"開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。"</code>
SlotKeeperは、開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-03-AC"</code> 前提: 過去・30日超・日本時間の日跨ぎの入力がある。条件: 時刻を検証する。期待結果: 422とし、翌日00:00終了も拒否する。
  - criterion(JSON Object): <code>{"given":"過去・30日超・日本時間の日跨ぎの入力がある","id":"RULE-03-AC","then":"422とし、翌日00:00終了も拒否する","when":"時刻を検証する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-04: 保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。

要件ID(JSON): <code>"RULE-04"</code>
タイトル(JSON): <code>"保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。"</code>
SlotKeeperは、保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-04-AC"</code> 前提: 公開APIとClock依存がある。条件: OpenAPIと日本時間の変換を検査する。期待結果: 現在時刻を上書きする入力はなく、日本時間の日付境界で変換する。
  - criterion(JSON Object): <code>{"given":"公開APIとClock依存がある","id":"RULE-04-AC","then":"現在時刻を上書きする入力はなく、日本時間の日付境界で変換する","when":"OpenAPIと日本時間の変換を検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","frontend/src/logic.ts"]</code>
- テスト: <code>["frontend/tests/logic.test.ts","tests/app/apis/reservations/create_reservation/test_functions.py","tests/test_api_error_responses.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-05: 予約状態は &#96;confirmed → cancelled&#96; です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。

要件ID(JSON): <code>"RULE-05"</code>
タイトル(JSON): <code>"予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。"</code>
SlotKeeperは、予約状態は &#96;confirmed → cancelled&#96; です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-05-AC"</code> 前提: 確定予約がある。条件: 公開APIを検査して取消する。期待結果: 予約日時の直接編集APIはなく、状態はconfirmedからcancelledへだけ遷移する。
  - criterion(JSON Object): <code>{"given":"確定予約がある","id":"RULE-05-AC","then":"予約日時の直接編集APIはなく、状態はconfirmedからcancelledへだけ遷移する","when":"公開APIを検査して取消する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/test_api_error_responses.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-06: 取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。

要件ID(JSON): <code>"RULE-06"</code>
タイトル(JSON): <code>"取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。"</code>
SlotKeeperは、取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-06-AC"</code> 前提: 確定予約がある。条件: 取消と同じ枠の再予約を行う。期待結果: 取消済みは重複判定から除かれ、確定予約は最大1件。
  - criterion(JSON Object): <code>{"given":"確定予約がある","id":"RULE-06-AC","then":"取消済みは重複判定から除かれ、確定予約は最大1件","when":"取消と同じ枠の再予約を行う"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_functions.py","tests/app/apis/reservations/cancel_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-07: 既定の「将来予約」は &#96;confirmed AND start_at &gt; now&#96; とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。

要件ID(JSON): <code>"RULE-07"</code>
タイトル(JSON): <code>"既定の「将来予約」は `confirmed AND start_at &gt; now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"既定の「将来予約」は `confirmed AND start_at &gt; now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。"</code>
SlotKeeperは、既定の「将来予約」は &#96;confirmed AND start_at &gt; now&#96; とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-07-AC"</code> 前提: 開始済みの予約がある資源。条件: 資源を無効化し将来予約を一覧する。期待結果: 無効化でき既存記録を保持し、将来予約はconfirmedかつ開始前だけ。
  - criterion(JSON Object): <code>{"given":"開始済みの予約がある資源","id":"RULE-07-AC","then":"無効化でき既存記録を保持し、将来予約はconfirmedかつ開始前だけ","when":"資源を無効化し将来予約を一覧する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/resources/update_resource/router.py","src/app/apis/resources/update_resource/functions.py","src/app/apis/reservations/list_reservations/sql/001_select_reservations.sql"]</code>
- テスト: <code>["tests/app/apis/reservations/list_reservations/test_router.py","tests/app/apis/resources/update_resource/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-08: 将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。

要件ID(JSON): <code>"RULE-08"</code>
タイトル(JSON): <code>"将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。"</code>
SlotKeeperは、将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-08-AC"</code> 前提: 将来予約がある資源、または予約作成と無効化の同時実行。条件: 無効化する。期待結果: 無効資源に将来予約を残さない。
  - criterion(JSON Object): <code>{"given":"将来予約がある資源、または予約作成と無効化の同時実行","id":"RULE-08-AC","then":"無効資源に将来予約を残さない","when":"無効化する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/resources/update_resource/test_functions.py","tests/app/apis/resources/update_resource/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-09: 一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。

要件ID(JSON): <code>"RULE-09"</code>
タイトル(JSON): <code>"一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。"</code>
SlotKeeperは、一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-09-AC"</code> 前提: 他人の予約がある。条件: 一般利用者が予約表と詳細を取得し、管理者が詳細を取得する。期待結果: 一般利用者へ目的・識別情報・履歴を返さず、管理者は閲覧できる。
  - criterion(JSON Object): <code>{"given":"他人の予約がある","id":"RULE-09-AC","then":"一般利用者へ目的・識別情報・履歴を返さず、管理者は閲覧できる","when":"一般利用者が予約表と詳細を取得し、管理者が詳細を取得する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/resources/get_resource_schedule/router.py","src/app/apis/resources/get_resource_schedule/functions.py","src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/get_reservation/test_functions.py","tests/app/apis/reservations/get_reservation/test_router.py","tests/app/apis/resources/get_resource_schedule/test_functions.py","tests/app/apis/resources/get_resource_schedule/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-10: 予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。

要件ID(JSON): <code>"RULE-10"</code>
タイトル(JSON): <code>"予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。"</code>
SlotKeeperは、予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-10-AC"</code> 前提: 同じ利用者の要求キーがある。条件: 同じ入力・異なる入力・24時間後に再送する。期待結果: 元の成功応答・409・新規要求として扱う。
  - criterion(JSON Object): <code>{"given":"同じ利用者の要求キーがある","id":"RULE-10-AC","then":"元の成功応答・409・新規要求として扱う","when":"同じ入力・異なる入力・24時間後に再送する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-11: 成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。

要件ID(JSON): <code>"RULE-11"</code>
タイトル(JSON): <code>"成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。"</code>
SlotKeeperは、成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-11-AC"</code> 前提: 作成済み予約が取消または開始済みである。条件: 24時間以内に同じキーで再送する。期待結果: 時刻検証より先に照合し元の作成結果を返す。
  - criterion(JSON Object): <code>{"given":"作成済み予約が取消または開始済みである","id":"RULE-11-AC","then":"時刻検証より先に照合し元の作成結果を返す","when":"24時間以内に同じキーで再送する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-12: 予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。

要件ID(JSON): <code>"RULE-12"</code>
タイトル(JSON): <code>"予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。"</code>
SlotKeeperは、予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-12-AC"</code> 前提: 作成または取消の途中で障害が起きる。条件: 操作を確定する。期待結果: 予約・履歴・要求キーを同一transactionで確定またはrollbackする。
  - criterion(JSON Object): <code>{"given":"作成または取消の途中で障害が起きる","id":"RULE-12-AC","then":"予約・履歴・要求キーを同一transactionで確定またはrollbackする","when":"操作を確定する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_functions.py","tests/app/apis/reservations/cancel_reservation/test_router.py","tests/app/apis/reservations/create_reservation/test_functions.py","tests/app/apis/reservations/create_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-13: 取消済み予約への取消は409とします。履歴を追加しません。

要件ID(JSON): <code>"RULE-13"</code>
タイトル(JSON): <code>"取消済み予約への取消は409とします。履歴を追加しません。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"取消済み予約への取消は409とします。履歴を追加しません。"</code>
SlotKeeperは、取消済み予約への取消は409とします。履歴を追加しません。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-13-AC"</code> 前提: 取消済み予約がある。条件: 取消する。期待結果: 409で履歴を追加しない。
  - criterion(JSON Object): <code>{"given":"取消済み予約がある","id":"RULE-13-AC","then":"409で履歴を追加しない","when":"取消する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/cancel_reservation/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

## RULE-14: 資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。

要件ID(JSON): <code>"RULE-14"</code>
タイトル(JSON): <code>"資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。"</code>
SlotKeeperは、資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。を**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 2 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"lazunex-alignment"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-14-AC"</code> 前提: 境界長の名前・説明・目的と複数ページの一覧がある。条件: 入力と一覧を検査する。期待結果: 長さ制約を守り、固定順とID順でページングする。
  - criterion(JSON Object): <code>{"given":"境界長の名前・説明・目的と複数ページの一覧がある","id":"RULE-14-AC","then":"長さ制約を守り、固定順とID順でページングする","when":"入力と一覧を検査する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: test
検証証跡: 品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する
検証(JSON Object): <code>{"evidence":"品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する","method":"test"}</code>
トレース(JSON List、順序保持):
- 設計: <code>["docs/spec/40.apis/index.md"]</code>
- 実装: <code>["src/app/apis/common.py","src/app/apis/reservations/create_reservation/functions.py","src/app/apis/reservations/create_reservation/router.py"]</code>
- テスト: <code>["tests/app/apis/reservations/list_reservations/test_functions.py","tests/app/apis/reservations/list_reservations/test_router.py","tests/app/apis/resources/create_resource/test_functions.py","tests/app/apis/resources/create_resource/test_router.py","tests/app/apis/resources/list_resources/test_functions.py","tests/app/apis/resources/list_resources/test_router.py"]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

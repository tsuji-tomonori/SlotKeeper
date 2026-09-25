<!-- tools/quintflow.pyによる自動生成。spec/requirements/requirements.qntを編集すること。 -->
# SlotKeeper 要件一覧

- スキーマ版: 1
- カタログ版: 1
- Product(JSON): <code>"SlotKeeper"</code>
- 更新日(JSON): <code>"2026-09-25"</code>
- 正本: `spec/requirements/requirements.qnt`
- 機械可読view: `spec/requirements/requirements.json`

| ID | 版 | 状態 | 種別 | 原子的な義務 | 検証方法 |
|---|---:|---|---|---|---|
| <code>"COM-01"</code> | 1 | 有効 | 機能 | SlotKeeperは、幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-02"</code> | 1 | 有効 | 機能 | SlotKeeperは、確定済みのデータは再起動後も残る。失敗操作で部分更新を残さないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-03"</code> | 1 | 有効 | 機能 | SlotKeeperは、入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-04"</code> | 1 | 有効 | 機能 | SlotKeeperは、サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-05"</code> | 1 | 有効 | 機能 | SlotKeeperは、起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-06"</code> | 1 | 有効 | 機能 | SlotKeeperは、資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-07"</code> | 1 | 有効 | 機能 | SlotKeeperは、要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"COM-08"</code> | 1 | 有効 | 機能 | SlotKeeperは、空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-01"</code> | 1 | 有効 | 機能 | SlotKeeperは、管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-02"</code> | 1 | 有効 | 機能 | SlotKeeperは、資源と日付を指定して、その日の予約済み時間帯を確認できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-03"</code> | 1 | 有効 | 機能 | SlotKeeperは、資源、開始・終了、目的を指定して、自分名義の予約を作成できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-04"</code> | 1 | 有効 | 機能 | SlotKeeperは、同一資源の予約済み時間と重なる予約の確定を拒否するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-05"</code> | 1 | 有効 | 機能 | SlotKeeperは、本人または管理者が、開始前の予約を取消できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-06"</code> | 1 | 有効 | 機能 | SlotKeeperは、自分の予約を日付・状態で絞り込めるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-07"</code> | 1 | 有効 | 機能 | SlotKeeperは、作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"SLOT-08"</code> | 1 | 有効 | 機能 | SlotKeeperは、要求の再送を識別し、予約と履歴を二重に作らないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-STACK"</code> | 1 | 有効 | 制約 | SlotKeeperは、Astro静的フロントとFastAPIを使用するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-DB"</code> | 1 | 有効 | 制約 | SlotKeeperは、DSQLとPostgreSQLで共通の予約不変条件を守るを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-AUTH"</code> | 1 | 有効 | 制約 | SlotKeeperは、署名、issuer、client、用途、期限を検査するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-LAMBDA"</code> | 1 | 有効 | 制約 | SlotKeeperは、依存を含むLinux用Lambda ZIPを作成するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-INFRA"</code> | 1 | 有効 | 制約 | SlotKeeperは、Python CDKで常設サーバーを持たない構成を合成するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-COMPOSE"</code> | 1 | 有効 | 制約 | SlotKeeperは、GitとDocker Composeだけで起動と全検証を行えるを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-DESIGN"</code> | 1 | 有効 | 制約 | SlotKeeperは、実装から6帳票、DB、CRUD、画面、infraを決定的に生成するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-PORTAL"</code> | 1 | 有効 | 制約 | SlotKeeperは、同一revisionとrunの実測結果と設計をPagesへ集約するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-PERF"</code> | 1 | 有効 | 制約 | SlotKeeperは、指定負荷とデータ量でAPI別の性能を測定するを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-QUALITY"</code> | 1 | 有効 | 制約 | SlotKeeperは、型、lint、実DB、ブラウザ、負例検査の失敗を隠さないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"TECH-PRIVACY"</code> | 1 | 有効 | 制約 | SlotKeeperは、公開allowlistに秘密や生ログを含めないを**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-01"</code> | 1 | 有効 | 制約 | SlotKeeperは、予約区間は &#96;[開始, 終了)&#96; とします。10:00〜11:00と11:00〜12:00は重複しません。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-02"</code> | 1 | 有効 | 制約 | SlotKeeperは、開始・終了は15分刻み、予約時間は15分以上4時間以下です。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-03"</code> | 1 | 有効 | 制約 | SlotKeeperは、開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-04"</code> | 1 | 有効 | 制約 | SlotKeeperは、保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-05"</code> | 1 | 有効 | 制約 | SlotKeeperは、予約状態は &#96;confirmed → cancelled&#96; です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-06"</code> | 1 | 有効 | 制約 | SlotKeeperは、取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-07"</code> | 1 | 有効 | 制約 | SlotKeeperは、既定の「将来予約」は &#96;confirmed AND start_at &gt; now&#96; とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-08"</code> | 1 | 有効 | 制約 | SlotKeeperは、将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-09"</code> | 1 | 有効 | 制約 | SlotKeeperは、一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-10"</code> | 1 | 有効 | 制約 | SlotKeeperは、予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-11"</code> | 1 | 有効 | 制約 | SlotKeeperは、成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-12"</code> | 1 | 有効 | 制約 | SlotKeeperは、予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-13"</code> | 1 | 有効 | 制約 | SlotKeeperは、取消済み予約への取消は409とします。履歴を追加しません。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |
| <code>"RULE-14"</code> | 1 | 有効 | 制約 | SlotKeeperは、資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。を**提供する**（<code>"provide"</code>） | 実装と受入テストの照合 |

## COM-01: 幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない

要件ID(JSON): <code>"COM-01"</code>
タイトル(JSON): <code>"幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない"</code>
主体(JSON): <code>"SlotKeeper"</code>
対象(JSON): <code>"幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない"</code>
SlotKeeperは、幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さないを**提供する**。
行為enum: <code>"provide"</code>

根拠: 利用者が指定した初回受入の永続義務
根拠(JSON): <code>"利用者が指定した初回受入の永続義務"</code>

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-01-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-01-AC","then":"幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-02-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-02-AC","then":"確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-03-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-03-AC","then":"入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-04-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-04-AC","then":"サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-05-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-05-AC","then":"起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-06-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-06-AC","then":"資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-07-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-07-AC","then":"要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"COM-08-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"COM-08-AC","then":"空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-01-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-01-AC","then":"管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-02-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 資源と日付を指定して、その日の予約済み時間帯を確認できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-02-AC","then":"資源と日付を指定して、その日の予約済み時間帯を確認できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-03-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 資源、開始・終了、目的を指定して、自分名義の予約を作成できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-03-AC","then":"資源、開始・終了、目的を指定して、自分名義の予約を作成できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-04-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 同一資源の予約済み時間と重なる予約の確定を拒否する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-04-AC","then":"同一資源の予約済み時間と重なる予約の確定を拒否する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-05-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 本人または管理者が、開始前の予約を取消できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-05-AC","then":"本人または管理者が、開始前の予約を取消できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-06-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 自分の予約を日付・状態で絞り込める。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-06-AC","then":"自分の予約を日付・状態で絞り込める","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-07-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-07-AC","then":"作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `functional`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"functional"</code>

受入条件:
- <code>"SLOT-08-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 要求の再送を識別し、予約と履歴を二重に作らない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"SLOT-08-AC","then":"要求の再送を識別し、予約と履歴を二重に作らない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-STACK-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: Astro静的フロントとFastAPIを使用する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-STACK-AC","then":"Astro静的フロントとFastAPIを使用する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-DB-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: DSQLとPostgreSQLで共通の予約不変条件を守る。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-DB-AC","then":"DSQLとPostgreSQLで共通の予約不変条件を守る","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-AUTH-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 署名、issuer、client、用途、期限を検査する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-AUTH-AC","then":"署名、issuer、client、用途、期限を検査する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-LAMBDA-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 依存を含むLinux用Lambda ZIPを作成する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-LAMBDA-AC","then":"依存を含むLinux用Lambda ZIPを作成する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-INFRA-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: Python CDKで常設サーバーを持たない構成を合成する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-INFRA-AC","then":"Python CDKで常設サーバーを持たない構成を合成する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-COMPOSE-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: GitとDocker Composeだけで起動と全検証を行える。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-COMPOSE-AC","then":"GitとDocker Composeだけで起動と全検証を行える","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-DESIGN-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 実装から6帳票、DB、CRUD、画面、infraを決定的に生成する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-DESIGN-AC","then":"実装から6帳票、DB、CRUD、画面、infraを決定的に生成する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PORTAL-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 同一revisionとrunの実測結果と設計をPagesへ集約する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-PORTAL-AC","then":"同一revisionとrunの実測結果と設計をPagesへ集約する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PERF-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 指定負荷とデータ量でAPI別の性能を測定する。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-PERF-AC","then":"指定負荷とデータ量でAPI別の性能を測定する","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-QUALITY-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 型、lint、実DB、ブラウザ、負例検査の失敗を隠さない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-QUALITY-AC","then":"型、lint、実DB、ブラウザ、負例検査の失敗を隠さない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"project"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"TECH-PRIVACY-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 公開allowlistに秘密や生ログを含めない。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"TECH-PRIVACY-AC","then":"公開allowlistに秘密や生ログを含めない","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>[]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-01-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 予約区間は &#96;[開始, 終了)&#96; とします。10:00〜11:00と11:00〜12:00は重複しません。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-01-AC","then":"予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-02-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 開始・終了は15分刻み、予約時間は15分以上4時間以下です。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-02-AC","then":"開始・終了は15分刻み、予約時間は15分以上4時間以下です。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-03-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-03-AC","then":"開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-04-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-04-AC","then":"保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-05-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 予約状態は &#96;confirmed → cancelled&#96; です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-05-AC","then":"予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-06-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-06-AC","then":"取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-07-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 既定の「将来予約」は &#96;confirmed AND start_at &gt; now&#96; とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-07-AC","then":"既定の「将来予約」は `confirmed AND start_at &gt; now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-08-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-08-AC","then":"将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-09-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-09-AC","then":"一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-10-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-10-AC","then":"予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-11-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-11-AC","then":"成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-12-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-12-AC","then":"予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-13-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 取消済み予約への取消は409とします。履歴を追加しません。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-13-AC","then":"取消済み予約への取消は409とします。履歴を追加しません。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
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

項目版: 1 / 状態: `active` / 種別: `constraint`
変更識別子: <code>"initial-implementation"</code>
分類: scope=<code>"product"</code> / category=<code>"nonfunctional"</code>

受入条件:
- <code>"RULE-14-AC"</code> 前提: 対応する入力、権限、状態がある。条件: 仕様に対応する操作または検証を実行する。期待結果: 資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。。
  - criterion(JSON Object): <code>{"given":"対応する入力、権限、状態がある","id":"RULE-14-AC","then":"資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。","when":"仕様に対応する操作または検証を実行する"}</code>

要求源(JSON List): <code>["IMPLEMENTATION_REQUEST.md"]</code>
検証方法: 実装と受入テストの照合
検証証跡: 同一runのcollectorと結果を品質ポータルに掲載
検証(JSON Object): <code>{"evidence":"同一runのcollectorと結果を品質ポータルに掲載","method":"実装と受入テストの照合"}</code>
トレース(JSON List、順序保持):
- 設計: <code>[]</code>
- 実装: <code>["backend/src/slotkeeper/app.py"]</code>
- テスト: <code>[]</code>
- 参照資料: <code>["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"]</code>
廃止理由: <code>""</code>
後継要件: <code>""</code>

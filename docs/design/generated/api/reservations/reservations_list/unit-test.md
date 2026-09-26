# reservations_list / Unit Test

## 0. endpoint層の暗黙処理

FastAPI入力解析と認証依存を適用。

## 1. 要因ごとの要素

### 入力・権限・状態・競合

実在ケースだけを列挙する。全組合せの網羅を意味しない。

## 2. 組合せたテストケース一覧

| ID | 受入説明 |
| --- | --- |
| backend/tests/test_auth.py::test_bad_claims | Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_bad_signature | Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_anonymous_and_health | Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04-AC] [COM-03-AC] |
| backend/tests/test_auth.py::test_user_cannot_create_resource | Given 一般利用者 When 管理API Then 403。 [SLOT-01-AC] [COM-04-AC] |
| backend/tests/test_auth.py::test_cognito_access_and_id | Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14] |
| backend/tests/test_reservations.py::test_create_adjacent_overlap | Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02] [RULE-01-AC] |
| backend/tests/test_reservations.py::test_privacy_and_cancel | Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] [SLOT-02-AC] [RULE-09-AC] [RULE-13-AC] [RULE-06-AC] [COM-04-AC] |
| backend/tests/test_reservations.py::test_replay_before_validation | Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15] [RULE-10-AC] |
| backend/tests/test_reservations.py::test_replay_after_start | Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15] [RULE-11-AC] |
| backend/tests/test_reservations.py::test_versions_and_inactive | Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11] |
| backend/tests/test_reservations.py::test_future_prevents_disable | Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] [RULE-08-AC] |
| backend/tests/test_reservations.py::test_cancel_boundaries | Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] [RULE-13-AC] |
| backend/tests/test_reservations.py::test_twenty_concurrent | Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 [SLOT-AC03] |
| backend/tests/test_reservations.py::test_same_key_concurrent | Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 [SLOT-AC07] |
| backend/tests/test_reservations.py::test_create_vs_disable | Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] [RULE-08-AC] |
| backend/tests/test_reservations.py::test_rollback_at_event | Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12] [RULE-12-AC] [COM-02-AC] |
| backend/tests/test_reservations.py::test_disable_after_start_keeps_record | Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 [RULE-07-AC] |
| backend/tests/test_reservations.py::test_repeatable_read | Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02-AC] [TECH-DB-AC] |
| backend/tests/test_reservations.py::test_list_filters_only_own | Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 [SLOT-AC08] [RULE-07-AC] |
| backend/tests/test_reservations.py::test_admin_cancels_other_before_start | Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 [SLOT-AC04] [SLOT-07-AC] [RULE-09-AC] |
| backend/tests/test_reservations.py::test_cancel_and_rebook_concurrent | Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 [RULE-06-AC] |
| backend/tests/test_reservations.py::test_invalid_token_leaves_database | Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 [SLOT-AC14] |
| backend/tests/test_reservations.py::test_migrate_and_seed_repeat | Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 [COM-05-AC] [COM-02-AC] [SLOT-AC16] |
| backend/tests/test_reservations.py::test_resource_paging_order | Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 [SLOT-01-AC] [RULE-14-AC] |

## 3. テスト詳細

### backend/tests/test_auth.py::test_bad_claims

Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14]

### backend/tests/test_auth.py::test_bad_signature

Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14]

### backend/tests/test_auth.py::test_anonymous_and_health

Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04-AC] [COM-03-AC]

### backend/tests/test_auth.py::test_user_cannot_create_resource

Given 一般利用者 When 管理API Then 403。 [SLOT-01-AC] [COM-04-AC]

### backend/tests/test_auth.py::test_cognito_access_and_id

Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14]

### backend/tests/test_reservations.py::test_create_adjacent_overlap

Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02] [RULE-01-AC]

### backend/tests/test_reservations.py::test_privacy_and_cancel

Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] [SLOT-02-AC] [RULE-09-AC] [RULE-13-AC] [RULE-06-AC] [COM-04-AC]

### backend/tests/test_reservations.py::test_replay_before_validation

Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15] [RULE-10-AC]

### backend/tests/test_reservations.py::test_replay_after_start

Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15] [RULE-11-AC]

### backend/tests/test_reservations.py::test_versions_and_inactive

Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11]

### backend/tests/test_reservations.py::test_future_prevents_disable

Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] [RULE-08-AC]

### backend/tests/test_reservations.py::test_cancel_boundaries

Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] [RULE-13-AC]

### backend/tests/test_reservations.py::test_twenty_concurrent

Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 [SLOT-AC03]

### backend/tests/test_reservations.py::test_same_key_concurrent

Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 [SLOT-AC07]

### backend/tests/test_reservations.py::test_create_vs_disable

Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] [RULE-08-AC]

### backend/tests/test_reservations.py::test_rollback_at_event

Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12] [RULE-12-AC] [COM-02-AC]

### backend/tests/test_reservations.py::test_disable_after_start_keeps_record

Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 [RULE-07-AC]

### backend/tests/test_reservations.py::test_repeatable_read

Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02-AC] [TECH-DB-AC]

### backend/tests/test_reservations.py::test_list_filters_only_own

Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 [SLOT-AC08] [RULE-07-AC]

### backend/tests/test_reservations.py::test_admin_cancels_other_before_start

Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 [SLOT-AC04] [SLOT-07-AC] [RULE-09-AC]

### backend/tests/test_reservations.py::test_cancel_and_rebook_concurrent

Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 [RULE-06-AC]

### backend/tests/test_reservations.py::test_invalid_token_leaves_database

Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 [SLOT-AC14]

### backend/tests/test_reservations.py::test_migrate_and_seed_repeat

Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 [COM-05-AC] [COM-02-AC] [SLOT-AC16]

### backend/tests/test_reservations.py::test_resource_paging_order

Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 [SLOT-01-AC] [RULE-14-AC]

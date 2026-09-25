# テスト設計

| 実在テスト | Given / When / Then |
| --- | --- |
| backend/tests/test_auth.py::test_bad_claims | Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_bad_signature | Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_anonymous_and_health | Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04] |
| backend/tests/test_auth.py::test_user_cannot_create_resource | Given 一般利用者 When 管理API Then 403。 [SLOT-01] |
| backend/tests/test_auth.py::test_cognito_access_and_id | Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14] |
| backend/tests/test_domain.py::test_reject_invalid_time | Given 範囲外または刻み不正 When 時刻検証 Then 入力不正。 [SLOT-AC06] |
| backend/tests/test_domain.py::test_boundaries | Given 15分・4時間・30日境界 When 時刻検証 Then 受け付ける。 [SLOT-AC06] |
| backend/tests/test_domain.py::test_resource_input | Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 [COM-03] |
| backend/tests/test_domain.py::test_normalized_input | Given 同じ瞬間のoffset差と前後空白 When 正規化 Then 同一要求。 [SLOT-AC09] |
| backend/tests/test_lambda.py::test_gateway_event | Given HTTP APIイベント When Mangum変換 Then health200・未認証業務401。 [TECH-LAMBDA] |
| backend/tests/test_lambda.py::test_distribution_zip | Given 配布ZIP When 隔離pathからimport Then SQLと依存を含むhandlerを読める。 [TECH-LAMBDA] |
| backend/tests/test_reservations.py::test_create_adjacent_overlap | Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 [SLOT-AC01] [SLOT-AC02] |
| backend/tests/test_reservations.py::test_privacy_and_cancel | Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 [SLOT-AC04] [SLOT-AC08] |
| backend/tests/test_reservations.py::test_replay_before_validation | Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 [SLOT-AC07] [SLOT-AC09] [SLOT-AC15] |
| backend/tests/test_reservations.py::test_replay_after_start | Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 [SLOT-AC15] |
| backend/tests/test_reservations.py::test_versions_and_inactive | Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 [SLOT-AC05] [SLOT-AC11] |
| backend/tests/test_reservations.py::test_future_prevents_disable | Given 将来の確定予約 When 無効化 Then 409。 [SLOT-AC05] |
| backend/tests/test_reservations.py::test_cancel_boundaries | Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 [SLOT-AC11] [SLOT-AC13] |
| backend/tests/test_reservations.py::test_twenty_concurrent | Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 [SLOT-AC03] |
| backend/tests/test_reservations.py::test_same_key_concurrent | Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 [SLOT-AC07] |
| backend/tests/test_reservations.py::test_create_vs_disable | Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 [SLOT-AC10] |
| backend/tests/test_reservations.py::test_rollback_at_event | Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 [SLOT-AC12] |
| backend/tests/test_reservations.py::test_repeatable_read | Given ローカル接続 When 分離レベル取得 Then repeatable read。 [COM-02] |

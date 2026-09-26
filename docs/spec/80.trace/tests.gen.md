# テスト設計

| テストID | 説明 | 受入条件 |
|---|---|---|
| tests/app/apis/reservations/cancel_reservation/test_functions.py::test_get_reservation_and_predicates | Given aliceの確定予約 When 取得と取消可否を判定 Then 本人と管理者だけ許可し版・状態・開始を判定する。 | SLOT-AC04, SLOT-AC11, SLOT-AC13 |
| tests/app/apis/reservations/cancel_reservation/test_functions.py::test_cancel_updates_and_appends_event | Given 取消可能な予約 When 制御版・状態・履歴を更新 Then 取消済みの版2と取消履歴を返す。 | RULE-12-AC, RULE-06-AC |
| tests/app/apis/reservations/cancel_reservation/test_functions.py::test_rejection_builders | Given 権限なし・古い版・取消済み・開始済み When 拒否応答を組み立てる Then 403と409の理由コードを返す。 | SLOT-AC04, SLOT-AC11, SLOT-AC13 |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_privacy_and_cancel | Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 | SLOT-AC04, SLOT-AC08, SLOT-02-AC, RULE-09-AC, RULE-13-AC, RULE-06-AC, COM-04-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_cancel_boundaries | Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 | SLOT-AC11, SLOT-AC13, RULE-13-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_admin_cancels_other_before_start | Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 | SLOT-AC04, SLOT-07-AC, RULE-09-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_cancel_and_rebook_concurrent | Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 | RULE-06-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_missing_reservation_returns_404 | Given 存在しない予約 When 取消 Then 404で区別する。 | COM-03-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_cancel_reservation_router_returns_sample_shaped_response_with_db | Given 開始前の確定予約 When 標本requestで取消 Then 標本と同じ形の応答を返し取消と履歴を保存する。 | SLOT-AC04, RULE-12-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_cancel_reservation_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 予約取消 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc001_cancel_reservation_router_matches_unit_test_gen | Given aliceの予約 When bobが取消 Then 403で運用ログを出す。 | SLOT-AC04, COM-04-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc002_cancel_reservation_router_matches_unit_test_gen | Given 版1の予約 When 版2で取消 Then 409で運用ログを出す。 | SLOT-AC11 |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc003_cancel_reservation_router_matches_unit_test_gen | Given 取消済みの予約 When 最新版で再取消 Then 409で運用ログを出す。 | SLOT-AC13, RULE-13-AC |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc004_cancel_reservation_router_matches_unit_test_gen | Given 開始時刻を迎えた予約 When 取消 Then 409で運用ログを出す。 | SLOT-AC13 |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc005_cancel_reservation_router_matches_unit_test_gen | Given 開始前の確定予約 When 本人が取消 Then 200で取消済みを返す。 | SLOT-AC04 |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc006_cancel_reservation_router_matches_unit_test_gen | Given 予約取消の対象取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc007_cancel_reservation_router_matches_unit_test_gen | Given 予約取消の対象取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/cancel_reservation/test_router.py::test_tc008_cancel_reservation_router_matches_unit_test_gen | Given 予約取消の対象取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_reject_invalid_time | Given 範囲外または刻み不正 When 時刻検証 Then 入力不正。 | SLOT-AC06, RULE-02-AC, RULE-03-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_boundaries | Given 15分・4時間・30日境界 When 時刻検証 Then 受け付ける。 | SLOT-AC06, RULE-02-AC, RULE-03-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_normalized_input | Given 同じ瞬間のoffset差と前後空白 When 正規化 Then 同一要求。 | SLOT-AC09 |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_expired_record_is_not_replayed | Given 期限切れの成功記録 When 再送判定 Then 元応答を返さず新規要求として扱う。 | SLOT-AC15, RULE-10-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_request_rejects_unknown_fields | Given 公開契約にない項目 When 予約作成の入力解析 Then 拒否する。 | COM-03-AC, RULE-04-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_get_idempotency_record_marks_expiry | Given 期限切れと未登録の要求キー When 成功記録を取得 Then 期限切れを区別し未登録は空の参照を返す。 | SLOT-AC15 |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_update_resource_control_version_locks_or_404 | Given 存在する資源と存在しない資源 When 内部制御版を進める Then 資源参照か404を返す。 | SLOT-AC10 |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_has_overlapping_reservation_uses_half_open_interval | Given 重なる確定予約の件数 When 重複を判定 Then 開始と終了を半開区間の条件として渡す。 | RULE-01-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_save_reservation_owner_event_and_record | Given 検証済み要求 When 利用者・予約・履歴・成功記録を保存 Then 同じ予約と要求hashで記録する。 | RULE-12-AC |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_rejection_builders_return_conflicts | Given 再送誤用・無効資源・重複 When 拒否応答を組み立てる Then それぞれ409と理由コードを返す。 | SLOT-AC02, SLOT-AC05, SLOT-AC09 |
| tests/app/apis/reservations/create_reservation/test_functions.py::test_router_error_response_maps_exceptions | Given Routerで捕捉した業務例外 When error responseへ変換 Then 例外のstatusと理由を返す。 | COM-03-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_create_adjacent_overlap | Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 | SLOT-AC01, SLOT-AC02, RULE-01-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_replay_before_validation | Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 | SLOT-AC07, SLOT-AC09, SLOT-AC15, RULE-10-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_replay_after_start | Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 | SLOT-AC15, RULE-11-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_twenty_concurrent | Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 | SLOT-AC03 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_same_key_concurrent | Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 | SLOT-AC07 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_rollback_at_event | Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 | SLOT-AC12, RULE-12-AC, COM-02-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_invalid_token_leaves_database | Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 | SLOT-AC14 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_create_status_codes | Given 不正入力・対象なし・キーなし When 予約作成 Then 422・404・422を区別し入力値を反射しない。 | COM-03-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_rule_violation_is_422 | Given 15分刻みでない時刻 When 予約作成 Then 422で予約を作らない。 | SLOT-AC06, RULE-02-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_create_reservation_router_returns_sample_shaped_response_with_db | Given 標本request When 予約作成 Then 標本と同じ形の応答を返し予約・履歴・成功記録・利用者を保存する。 | SLOT-AC01, RULE-12-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_create_reservation_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 予約作成 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc001_create_reservation_router_matches_unit_test_gen | Given 成功済みの要求キー When 異なる入力で再送 Then 409で運用ログを出す。 | SLOT-AC09, RULE-10-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc002_create_reservation_router_matches_unit_test_gen | Given 成功済みの要求キー When 同じ入力で再送 Then 201で元の応答を返し予約を増やさない。 | SLOT-AC07, RULE-10-AC |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc003_create_reservation_router_matches_unit_test_gen | Given 無効化した資源 When 予約作成 Then 409で運用ログを出す。 | SLOT-AC05 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc004_create_reservation_router_matches_unit_test_gen | Given 同じ時間帯の確定予約 When 予約作成 Then 409で運用ログを出す。 | SLOT-AC02 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc005_create_reservation_router_matches_unit_test_gen | Given 空き枠 When 予約作成 Then 201で確定予約を返す。 | SLOT-AC01 |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc006_create_reservation_router_matches_unit_test_gen | Given 予約作成の再送照合で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc007_create_reservation_router_matches_unit_test_gen | Given 予約作成の再送照合で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/create_reservation/test_router.py::test_tc008_create_reservation_router_matches_unit_test_gen | Given 予約作成の再送照合でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/get_reservation/test_functions.py::test_get_reservation_with_events | Given 予約と作成・取消履歴 When 詳細を取得 Then 本人と管理者だけが履歴つき詳細を参照できる。 | SLOT-07-AC, RULE-09-AC |
| tests/app/apis/reservations/get_reservation/test_functions.py::test_rejection_and_router_error_builders | Given 他人の予約とRouter例外 When 応答を組み立てる Then 403と例外のstatusを返す。 | COM-04-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_owner_and_admin_view_history | Given Aの予約 When 本人・管理者・他人が詳細取得 Then 本人と管理者は履歴を閲覧し他人は403。 | SLOT-07-AC, RULE-09-AC, COM-04-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_missing_reservation_returns_404 | Given 存在しない予約 When 詳細取得 Then 404で区別する。 | COM-03-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_get_reservation_router_returns_sample_shaped_response_with_db | Given aliceの予約 When 本人が詳細取得 Then 標本と同じ形で予約と作成履歴を返す。 | SLOT-07-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_get_reservation_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 予約詳細取得 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_tc001_get_reservation_router_matches_unit_test_gen | Given aliceの予約 When bobが詳細取得 Then 403で運用ログを出す。 | SLOT-07-AC, COM-04-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_tc002_get_reservation_router_matches_unit_test_gen | Given aliceの予約 When 管理者が詳細取得 Then 200で目的を含む詳細を返す。 | SLOT-07-AC, RULE-09-AC |
| tests/app/apis/reservations/get_reservation/test_router.py::test_tc003_get_reservation_router_matches_unit_test_gen | Given 予約詳細の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/get_reservation/test_router.py::test_tc004_get_reservation_router_matches_unit_test_gen | Given 予約詳細の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/get_reservation/test_router.py::test_tc005_get_reservation_router_matches_unit_test_gen | Given 予約詳細の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/list_reservations/test_functions.py::test_own_reservations_are_filtered_and_paged | Given 3件の予約と上限2件 When 本人の予約を日付で取得 Then 日本時間の日付範囲で問合せ継続tokenを付ける。 | SLOT-AC08, RULE-14-AC |
| tests/app/apis/reservations/list_reservations/test_functions.py::test_router_error_response | Given 不正な継続token When Router例外を変換 Then 422と理由コードを返す。 | COM-03-AC |
| tests/app/apis/reservations/list_reservations/test_router.py::test_list_filters_only_own | Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 | SLOT-AC08, RULE-07-AC |
| tests/app/apis/reservations/list_reservations/test_router.py::test_reservation_paging_order | Given 同じ日の3件の予約 When 継続tokenでページ単位に取得 Then 開始日時とIDの固定順で欠落・重複がない。 | RULE-14-AC |
| tests/app/apis/reservations/list_reservations/test_router.py::test_list_reservations_router_returns_sample_shaped_response_with_db | Given 利用者固有の予約1件 When 標本queryで一覧取得 Then 標本と同じ形で本人の予約だけを返す。 | SLOT-AC08 |
| tests/app/apis/reservations/list_reservations/test_router.py::test_list_reservations_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 予約一覧取得 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/reservations/list_reservations/test_router.py::test_tc001_list_reservations_router_matches_unit_test_gen | Given 予約のない利用者 When 一覧取得 Then 200で空の一覧を返す。 | SLOT-AC08 |
| tests/app/apis/reservations/list_reservations/test_router.py::test_tc002_list_reservations_router_matches_unit_test_gen | Given 予約一覧の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/list_reservations/test_router.py::test_tc003_list_reservations_router_matches_unit_test_gen | Given 予約一覧の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/reservations/list_reservations/test_router.py::test_tc004_list_reservations_router_matches_unit_test_gen | Given 予約一覧の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/create_resource/test_functions.py::test_resource_input | Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 | COM-03-AC, RULE-14-AC |
| tests/app/apis/resources/create_resource/test_functions.py::test_description_limit | Given 1,001文字の説明 When 入力解析 Then 拒否し1,000文字は受け付ける。 | RULE-14-AC |
| tests/app/apis/resources/create_resource/test_functions.py::test_only_admin_manages_resources | Given 一般利用者と管理者 When 資源管理権限を判定 Then 管理者だけ許可する。 | SLOT-01-AC, COM-04-AC |
| tests/app/apis/resources/create_resource/test_functions.py::test_save_resource_and_builders | Given 登録要求 When 資源を保存し応答を組み立てる Then 有効な初期版を返し保存失敗と権限不足を区別する。 | SLOT-01-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_user_cannot_create_resource | Given 一般利用者 When 管理API Then 403。 | SLOT-01-AC, COM-04-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_admin_creates_active_resource | Given 管理者 When 前後空白つきの資源名で登録 Then 201で空白を除き有効な初期版を返す。 | SLOT-01-AC, RULE-14-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_create_resource_router_returns_sample_shaped_response_with_db | Given 管理者 When 標本requestで資源登録 Then 標本と同じ形の応答を返し資源を保存する。 | SLOT-01-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_create_resource_sample_request_emits_router_error_log_to_stdio | Given 標本requestと保存中の業務例外 When 資源登録 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_tc001_create_resource_router_matches_unit_test_gen | Given 一般利用者 When 資源登録 Then 403で運用ログを出す。 | SLOT-01-AC, COM-04-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_tc002_create_resource_router_matches_unit_test_gen | Given 管理者 When 資源登録 Then 201で有効な資源を返す。 | SLOT-01-AC |
| tests/app/apis/resources/create_resource/test_router.py::test_tc003_create_resource_router_matches_unit_test_gen | Given 資源の保存で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/create_resource/test_router.py::test_tc004_create_resource_router_matches_unit_test_gen | Given 資源の保存で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/create_resource/test_router.py::test_tc005_create_resource_router_matches_unit_test_gen | Given 資源の保存でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/get_resource_schedule/test_functions.py::test_schedule_hides_other_details | Given aliceとbobの予約 When 予約表を組み立てる Then 本人と管理者だけに詳細を返し日本時間の日付で問い合わせる。 | SLOT-02-AC, RULE-09-AC |
| tests/app/apis/resources/get_resource_schedule/test_functions.py::test_router_error_response | Given 存在しない資源 When Router例外を変換 Then 404と理由コードを返す。 | COM-03-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_schedule_hides_other_details | Given Aの予約 When A・B・管理者が予約表を取得 Then Bには時間帯と予約済みだけを返す。 | SLOT-02-AC, RULE-09-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_missing_resource_returns_404 | Given 存在しない資源 When 予約表取得 Then 404で区別する。 | COM-03-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_get_resource_schedule_router_returns_sample_shaped_response_with_db | Given aliceとbobの予約 When aliceが標本queryで予約表取得 Then 標本と同じ形で自分の詳細だけを返す。 | SLOT-02-AC, RULE-09-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_get_resource_schedule_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 予約表取得 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_tc001_get_resource_schedule_router_matches_unit_test_gen | Given 予約のない資源 When 予約表取得 Then 200で空の予約表を返す。 | SLOT-02-AC |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_tc002_get_resource_schedule_router_matches_unit_test_gen | Given 予約表の資源取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_tc003_get_resource_schedule_router_matches_unit_test_gen | Given 予約表の資源取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/get_resource_schedule/test_router.py::test_tc004_get_resource_schedule_router_matches_unit_test_gen | Given 予約表の資源取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/list_resources/test_functions.py::test_resources_are_paged_by_name_and_id | Given 同名を含む3件の資源と上限2件 When 一覧を取得 Then 名前とIDの継続tokenで次ページを問い合わせる。 | SLOT-01-AC, RULE-14-AC |
| tests/app/apis/resources/list_resources/test_functions.py::test_router_error_response | Given 不正な継続token When Router例外を変換 Then 422と理由コードを返す。 | COM-03-AC |
| tests/app/apis/resources/list_resources/test_router.py::test_resource_paging_order | Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 | SLOT-01-AC, RULE-14-AC |
| tests/app/apis/resources/list_resources/test_router.py::test_list_resources_router_returns_sample_shaped_response_with_db | Given 先頭に並ぶ名前の資源 When 標本queryで一覧取得 Then 標本と同じ形で資源を返す。 | SLOT-01-AC |
| tests/app/apis/resources/list_resources/test_router.py::test_list_resources_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 資源一覧取得 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/resources/list_resources/test_router.py::test_tc001_list_resources_router_matches_unit_test_gen | Given 登録済みの資源 When 一覧取得 Then 200で資源を返す。 | SLOT-01-AC |
| tests/app/apis/resources/list_resources/test_router.py::test_tc002_list_resources_router_matches_unit_test_gen | Given 資源一覧の取得で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/list_resources/test_router.py::test_tc003_list_resources_router_matches_unit_test_gen | Given 資源一覧の取得で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/list_resources/test_router.py::test_tc004_list_resources_router_matches_unit_test_gen | Given 資源一覧の取得でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/update_resource/test_functions.py::test_permission_lock_version_and_future | Given 将来予約のある資源 When 権限・制御版・公開版・将来予約を判定 Then 無効化時だけ将来予約を問い合わせる。 | SLOT-AC05, SLOT-AC11, RULE-08-AC |
| tests/app/apis/resources/update_resource/test_functions.py::test_update_resource_and_builders | Given 編集要求 When 資源を更新し応答を組み立てる Then 公開版を進め拒否応答を区別する。 | SLOT-01-AC, SLOT-AC11 |
| tests/app/apis/resources/update_resource/test_router.py::test_versions_and_inactive | Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 | SLOT-AC05, SLOT-AC11 |
| tests/app/apis/resources/update_resource/test_router.py::test_future_prevents_disable | Given 将来の確定予約 When 無効化 Then 409。 | SLOT-AC05, RULE-08-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_create_vs_disable | Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 | SLOT-AC10, RULE-08-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_disable_after_start_keeps_record | Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 | RULE-07-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_missing_resource_returns_404 | Given 存在しない資源 When 編集 Then 404で区別する。 | COM-03-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_update_resource_router_returns_sample_shaped_response_with_db | Given 版1の資源 When 標本requestで編集 Then 標本と同じ形で版2の資源を返し保存する。 | SLOT-01-AC, SLOT-AC11 |
| tests/app/apis/resources/update_resource/test_router.py::test_update_resource_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 資源編集 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_tc001_update_resource_router_matches_unit_test_gen | Given 一般利用者 When 資源編集 Then 403で運用ログを出す。 | SLOT-01-AC, COM-04-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_tc002_update_resource_router_matches_unit_test_gen | Given 版1の資源 When 版2を指定して編集 Then 409で運用ログを出す。 | SLOT-AC11 |
| tests/app/apis/resources/update_resource/test_router.py::test_tc003_update_resource_router_matches_unit_test_gen | Given 将来予約のある資源 When 無効化 Then 409で運用ログを出す。 | SLOT-AC05, RULE-08-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_tc004_update_resource_router_matches_unit_test_gen | Given 将来予約のない資源 When 無効化 Then 200で無効な資源を返す。 | SLOT-01-AC |
| tests/app/apis/resources/update_resource/test_router.py::test_tc005_update_resource_router_matches_unit_test_gen | Given 資源編集の制御版更新で業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/update_resource/test_router.py::test_tc006_update_resource_router_matches_unit_test_gen | Given 資源編集の制御版更新で外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/resources/update_resource/test_router.py::test_tc007_update_resource_router_matches_unit_test_gen | Given 資源編集の制御版更新でHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/system/health/test_functions.py::test_build_health_response_returns_ok_only | Given 稼働中のAPI When 稼働状態を組み立てる Then 秘密やDB情報を含まずokだけを返す。 | TECH-PRIVACY-AC |
| tests/app/apis/system/health/test_functions.py::test_router_error_response | Given 稼働確認中の業務例外 When Router例外を変換 Then 500と理由コードを返す。 | COM-07-AC |
| tests/app/apis/system/health/test_router.py::test_health_router_returns_sample_shaped_response_with_db | Given 認証情報なし When 稼働確認 Then 標本と同じ稼働状態だけを返しDBを変更しない。 | TECH-PRIVACY-AC |
| tests/app/apis/system/health/test_router.py::test_health_sample_request_emits_router_error_log_to_stdio | Given 標本requestと処理中の業務例外 When 稼働確認 Then Router例外の運用ログをcatalogどおり出す。 | COM-07-AC |
| tests/app/apis/system/health/test_router.py::test_tc001_health_router_matches_unit_test_gen | Given 稼働中のAPI When 稼働確認 Then 200でokを返す。 | — |
| tests/app/apis/system/health/test_router.py::test_tc002_health_router_matches_unit_test_gen | Given 稼働状態の組立てで業務例外 When API呼出し Then Routerで500へ変換し運用ログを出す。 | — |
| tests/app/apis/system/health/test_router.py::test_tc003_health_router_matches_unit_test_gen | Given 稼働状態の組立てで外部API例外 When API呼出し Then Routerで502へ変換し運用ログを出す。 | — |
| tests/app/apis/system/health/test_router.py::test_tc004_health_router_matches_unit_test_gen | Given 稼働状態の組立てでHTTP例外 When API呼出し Then Routerで400へ変換し運用ログを出す。 | — |
| tests/app/apis/test_deps.py::test_bad_claims | Given 不正claim When 業務API呼出し Then 401でDB未接続。 | SLOT-AC14 |
| tests/app/apis/test_deps.py::test_bad_signature | Given 別の秘密鍵による改ざん When 検証 Then 401。 | SLOT-AC14 |
| tests/app/apis/test_deps.py::test_anonymous_and_health | Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 | COM-04-AC, COM-03-AC |
| tests/generated/test_reservations_cancel_reservation.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_reservations_create_reservation.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_reservations_get_reservation.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_reservations_list_reservations.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_resources_create_resource.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_resources_get_resource_schedule.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_resources_list_resources.py::test_generated_unit_case_is_documented | — | — |
| tests/generated/test_resources_update_resource.py::test_generated_unit_case_is_documented | — | — |
| tests/infra/test_stack.py::test_serverless_and_authorization | Given 配布ZIP When synth Then 公開bucketと常設サーバーがなく認証と削除保護がある。 | TECH-INFRA-AC |
| tests/infra/test_stack.py::test_routes_are_protected | Given HTTP API When routeを列挙 Then healthだけ認証なしで、他はJWTとaccess scopeが必須。 | TECH-INFRA-AC |
| tests/infra/test_stack.py::test_origin_consistency | Given 環境設定 When synth Then CORS・Cognito callback/logout・API許可元が同じ配信元を指す。 | TECH-INFRA-AC |
| tests/infra/test_stack.py::test_least_privilege_and_private_bucket | Given 合成IAMとbucket policy When 権限を列挙 Then DSQLは対象clusterのDbConnectだけでS3はCloudFrontだけ読める。 | TECH-INFRA-AC |
| tests/infra/test_stack.py::test_environment_settings | Given 環境context When synth Then ログ保持・throttle・環境名が設定どおりで削除保護は共通。 | TECH-INFRA-AC |
| tests/infra/test_stack.py::test_unknown_environment_rejected | Given 未定義や不正な環境名 When 設定を読む Then 推測で合成せず拒否する。 | TECH-INFRA-AC |
| tests/integrations/test_identity_provider.py::test_cognito_access_and_id | Given Cognito claim When accessとIDを検証 Then accessだけ受理。 | SLOT-AC14 |
| tests/integrations/test_identity_provider.py::test_jwks_client_is_bounded | Given 設定済みJWKS URL When 鍵取得clientを作る Then 短いtimeoutとcache寿命を持つ。 | SLOT-AC14 |
| tests/integrations/test_identity_provider.py::test_fake_verifier_rejects_unknown_token | Given 登録済みtokenだけを持つfake When 未登録tokenを検証 Then 拒否する。 | SLOT-AC14 |
| tests/test_api_error_responses.py::test_api_error_responses_are_selected_per_operation | Given 公開OpenAPI When 操作ごとのresponseを列挙 Then 業務上発生する状態だけを共通error schemaで宣言する。 | COM-03-AC |
| tests/test_api_error_responses.py::test_public_contract_has_no_clock_or_direct_edit | Given 公開OpenAPI When 入力と操作を列挙 Then 現在時刻の上書き入力と予約日時の直接編集がない。 | RULE-04-AC, RULE-05-AC |
| tests/test_db_session.py::test_transaction_retries_conflicts | Given commit時の直列化競合と一意性競合 When 処理順を実行 Then 新snapshotで再実行して成功する。 | SLOT-AC03, SLOT-AC07 |
| tests/test_db_session.py::test_transaction_limits | Given 解消しない競合と成否不明の切断 When 処理順を実行 Then 上限後503、再送安全でない処理は再試行しない。 | SLOT-AC12 |
| tests/test_db_session.py::test_business_errors_are_not_retried | Given 業務上の重複応答 When 処理順を実行 Then 再試行せずそのまま409を返す。 | SLOT-AC02 |
| tests/test_db_session.py::test_dsql_connection_uses_official_connector | Given DSQL設定 When engineを作る Then 公式connectorへIAM用の接続先・利用者とTLS検証を渡す。 | TECH-DB-AC |
| tests/test_db_session.py::test_repeatable_read | Given ローカル接続 When 分離レベル取得 Then repeatable read。 | COM-02-AC, TECH-DB-AC |
| tests/test_lambda_handler.py::test_gateway_event | Given HTTP APIイベント When Mangum変換 Then health200・未認証業務401。 | TECH-LAMBDA-AC |
| tests/test_lambda_handler.py::test_distribution_zip | Given 配布ZIP When 隔離pathからimport Then SQLと依存を含むhandlerを読める。 | TECH-LAMBDA-AC |
| tests/test_operational_logging.py::test_request_log_redacts | Given 目的とtokenを含む作成要求 When API呼出し Then 要求ID・operation・status・所要時間だけを記録する。 | COM-07-AC |
| tests/tools/test_app_tool_cli.py::test_docs_main_delegates_generate_tools | — | — |
| tests/tools/test_app_tool_cli.py::test_python_module_args_adds_check_for_docs_generator | — | — |
| tests/tools/test_app_tool_cli.py::test_python_module_args_adds_check_for_codegen_generator | — | — |
| tests/tools/test_app_tool_docs.py::test_rendered_tool_docs_include_all_registered_tools | — | — |
| tests/tools/test_app_tool_docs.py::test_generate_tool_docs_check_mode_detects_stale_outputs | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_accepts_matching_contract | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_rejects_operation_id_mismatch | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_rejects_slug_mismatch | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_rejects_missing_contract | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_rejects_invalid_literal_field | — | — |
| tests/tools/test_check_api_contracts.py::test_check_contracts_rejects_unsupported_auth_mode | — | — |
| tests/tools/test_check_api_descriptions.py::test_has_japanese_text_and_literal_string | — | — |
| tests/tools/test_check_api_descriptions.py::test_is_router_decorator_rejects_non_route_shapes | — | — |
| tests/tools/test_check_api_descriptions.py::test_ast_helpers_accept_supported_shapes | — | — |
| tests/tools/test_check_api_descriptions.py::test_enum_member_comment_rejects_missing_comment | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_router_file_accepts_japanese_summary_and_description | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_router_file_reports_missing_and_non_japanese_values | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_router_file_ignores_non_router_decorators | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_accepts_japanese_docstrings | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_reports_missing_and_non_japanese_docstrings | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_reports_placeholder_descriptions | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_reports_field_description_issues | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_accepts_enum_value_comments | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_schema_file_reports_enum_value_comment_issues | — | — |
| tests/tools/test_check_api_descriptions.py::test_check_api_descriptions_collects_router_and_schema_files | — | — |
| tests/tools/test_check_api_descriptions.py::test_render_issues_and_arg_parser_defaults | — | — |
| tests/tools/test_check_api_descriptions.py::test_main_exits_nonzero_when_issue_exists | — | — |
| tests/tools/test_check_api_descriptions.py::test_main_can_ignore_issue_exit_code | — | — |
| tests/tools/test_check_api_exception_summaries.py::test_check_api_exception_summaries_reports_missing_api_summary | — | — |
| tests/tools/test_check_api_exception_summaries.py::test_check_api_exception_summaries_accepts_summarized_errors | — | — |
| tests/tools/test_check_api_function_exception_policy.py::test_reports_wrong_exception_policy | — | — |
| tests/tools/test_check_api_function_exception_policy.py::test_accepts_business_errors_and_runtime_dependency_guards | — | — |
| tests/tools/test_check_api_function_names.py::test_load_rule_names_requires_descriptions | — | — |
| tests/tools/test_check_api_function_names.py::test_check_api_function_file_accepts_action_and_condition_names | — | — |
| tests/tools/test_check_api_function_names.py::test_check_api_function_file_reports_unknown_words_and_missing_docstring | — | — |
| tests/tools/test_check_api_function_names.py::test_check_api_function_names_accepts_repository_definitions | — | — |
| tests/tools/test_check_api_function_names.py::test_render_issues_and_main | — | — |
| tests/tools/test_check_api_function_names.py::test_build_arg_parser_defaults | — | — |
| tests/tools/test_check_api_function_resource_usage.py::test_reports_non_validation_function_without_resource_usage | — | — |
| tests/tools/test_check_api_function_resource_usage.py::test_allows_validation_and_explicit_resource_free_functions | — | — |
| tests/tools/test_check_api_function_resource_usage.py::test_accepts_queries_and_integration_resource_usage | — | — |
| tests/tools/test_check_api_function_tests.py::test_find_function_coverage_issues_detects_missing_test_reference | — | — |
| tests/tools/test_check_api_function_tests.py::test_find_function_coverage_issues_accepts_parametrized_case_names | — | — |
| tests/tools/test_check_api_managed_literals.py::test_check_api_managed_literals_reports_disallowed_literals | — | — |
| tests/tools/test_check_api_managed_literals.py::test_check_api_managed_literals_accepts_repository_usage | — | — |
| tests/tools/test_check_api_managed_literals.py::test_render_issues_and_main | — | — |
| tests/tools/test_check_api_managed_literals.py::test_build_arg_parser_defaults | — | — |
| tests/tools/test_check_api_mermaid_sequences.py::test_mermaid_blocks_extracts_body_and_start_line | — | — |
| tests/tools/test_check_api_mermaid_sequences.py::test_validate_file_accepts_generated_sequence_shape | — | — |
| tests/tools/test_check_api_mermaid_sequences.py::test_validate_file_rejects_message_colons_and_split_sql | — | — |
| tests/tools/test_check_api_mermaid_sequences.py::test_main_reports_issues | — | — |
| tests/tools/test_check_api_router_ignored_returns.py::test_reports_ignored_meaningful_return_and_read_side_effect | — | — |
| tests/tools/test_check_api_router_ignored_returns.py::test_accepts_used_returns_and_named_side_effects | — | — |
| tests/tools/test_check_api_router_test_asserts.py::test_read_crud_csv_and_mutation_tables | — | — |
| tests/tools/test_check_api_router_test_asserts.py::test_check_api_router_test_asserts_reports_missing_sample_and_table | — | — |
| tests/tools/test_check_api_router_test_asserts.py::test_check_api_router_test_asserts_accepts_repository_layout | — | — |
| tests/tools/test_check_api_router_test_asserts.py::test_main_and_arg_parser | — | — |
| tests/tools/test_check_api_router_tests.py::test_expected_router_test_path_mirrors_api_root | — | — |
| tests/tools/test_check_api_router_tests.py::test_check_api_router_tests_reports_missing_test_router | — | — |
| tests/tools/test_check_api_router_tests.py::test_check_api_router_tests_accepts_matching_test_router | — | — |
| tests/tools/test_check_api_router_tests.py::test_check_api_router_tests_accepts_repository_layout | — | — |
| tests/tools/test_check_api_router_tests.py::test_main_and_arg_parser | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_parse_unit_test_cases_extracts_expected_outcomes | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_expected_function_name_uses_tc_prefix | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_check_api_router_unit_test_factors_accepts_matching_cases | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_check_api_router_unit_test_factors_reports_missing_and_mismatch | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_check_api_router_unit_test_factors_rejects_helper_only_test | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_check_api_router_unit_test_factors_rejects_log_expectation_variables | — | — |
| tests/tools/test_check_api_router_unit_test_factors.py::test_arg_parser_defaults_and_main | — | — |
| tests/tools/test_check_api_sequence_success_responses.py::test_check_api_sequence_success_responses_reports_missing_2xx | — | — |
| tests/tools/test_check_api_sequence_success_responses.py::test_check_api_sequence_success_responses_accepts_2xx | — | — |
| tests/tools/test_check_api_sequence_success_responses.py::test_check_api_sequence_success_responses_reports_early_2xx | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_parse_sql_usage_collects_tables_aliases_and_mutation_columns | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_compare_usage_to_ddl_reports_both_directions | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_compare_usage_to_ddl_ignores_like_source_tables | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_compare_usage_to_ddl_ignores_hub_users_table | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_parse_sql_usage_collects_single_table_unqualified_columns | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_render_report_includes_locations_and_no_drift_message | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_check_and_arg_parser_defaults | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_main_exits_nonzero_when_drift_exists | — | — |
| tests/tools/test_check_api_sql_ddl_usage.py::test_main_can_ignore_drift_exit_code | — | — |
| tests/tools/test_check_bool_router_conditions.py::test_check_bool_router_conditions_reports_bare_await | — | — |
| tests/tools/test_check_bool_router_conditions.py::test_check_bool_router_conditions_accepts_if_conditions | — | — |
| tests/tools/test_check_constant_bool_returns.py::test_check_constant_bool_returns_reports_single_literal_value | — | — |
| tests/tools/test_check_exception_router_handlers.py::test_check_exception_router_handlers_reports_unhandled_calls | — | — |
| tests/tools/test_check_exception_router_handlers.py::test_check_exception_router_handlers_accepts_try_blocks | — | — |
| tests/tools/test_check_operational_logging.py::test_find_direct_logger_violations_reports_stdlib_logger_calls | — | — |
| tests/tools/test_check_operational_logging.py::test_check_operational_logging_accepts_wrapper_calls | — | — |
| tests/tools/test_check_router_error_response_returns.py::test_check_router_error_response_returns_reports_undeclared_status | — | — |
| tests/tools/test_check_router_error_response_returns.py::test_check_router_error_response_returns_accepts_declared_status | — | — |
| tests/tools/test_check_router_error_response_returns.py::test_check_router_error_response_returns_reports_exception_status | — | — |
| tests/tools/test_generate_api_detail_design.py::test_api_detail_design_extracts_normal_flow_details | — | — |
| tests/tools/test_generate_api_detail_design.py::test_api_detail_design_resolves_list_item_sources_to_db_columns | — | — |
| tests/tools/test_generate_api_list.py::test_collect_api_rows_outputs_compact_api_rows | — | — |
| tests/tools/test_generate_api_list.py::test_render_api_list_markdown_outputs_table | — | — |
| tests/tools/test_generate_api_list.py::test_generate_from_openapi_writes_api_list | — | — |
| tests/tools/test_generate_api_list.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_api_list.py::test_generate_loads_openapi_and_implementation_paths | — | — |
| tests/tools/test_generate_api_message_catalog.py::test_build_api_catalogs_reads_catalog_and_wrapper_calls | — | — |
| tests/tools/test_generate_api_message_catalog.py::test_generate_api_message_catalog_main_writes_and_checks_docs | — | — |
| tests/tools/test_generate_api_message_catalog.py::test_build_api_catalogs_reads_warning_messages_from_router_logger_call | — | — |
| tests/tools/test_generate_api_pytest_cases.py::test_unit_test_specs_extracts_case_ids | — | — |
| tests/tools/test_generate_api_pytest_cases.py::test_rendered_outputs_generate_collectable_pytest | — | — |
| tests/tools/test_generate_api_pytest_cases.py::test_generate_check_detects_changed_output | — | — |
| tests/tools/test_generate_api_sequences.py::test_sql_tables_extracts_ordered_unique_table_names | — | — |
| tests/tools/test_generate_api_sequences.py::test_function_target_accepts_action_and_predicate_names | — | — |
| tests/tools/test_generate_api_sequences.py::test_api_sequence_from_dir_reads_router_calls_and_sql | — | — |
| tests/tools/test_generate_api_sequences.py::test_function_metadata_reads_called_integration_resources | — | — |
| tests/tools/test_generate_api_sequences.py::test_query_sql_filenames_maps_called_query_to_sql | — | — |
| tests/tools/test_generate_api_sequences.py::test_endpoint_route_metadata_reads_path_method_and_responses | — | — |
| tests/tools/test_generate_api_sequences.py::test_implicit_router_error_returns_detects_auth_and_validation | — | — |
| tests/tools/test_generate_api_sequences.py::test_endpoint_error_returns_reads_router_error_schema_returns | — | — |
| tests/tools/test_generate_api_sequences.py::test_endpoint_exception_error_returns_reads_api_function_error_summaries | — | — |
| tests/tools/test_generate_api_sequences.py::test_endpoint_sequence_items_reads_router_error_handler_as_500 | — | — |
| tests/tools/test_generate_api_sequences.py::test_endpoint_route_metadata_handles_defaults_keyword_path_and_unknown_status | — | — |
| tests/tools/test_generate_api_sequences.py::test_transaction_step_from_await_reads_session_commit | — | — |
| tests/tools/test_generate_api_sequences.py::test_render_sequence_markdown_limits_resources_and_groups_tables | — | — |
| tests/tools/test_generate_api_sequences.py::test_query_sql_filenames_for_step_matches_query_function_suffix | — | — |
| tests/tools/test_generate_api_sequences.py::test_render_sequence_markdown_marks_transaction_scope_until_commit | — | — |
| tests/tools/test_generate_api_sequences.py::test_generate_sequences_and_check_mode | — | — |
| tests/tools/test_generate_api_sequences.py::test_helpers_cover_api_dirs_sql_steps_and_arg_parser | — | — |
| tests/tools/test_generate_api_sequences.py::test_query_sql_summaries_reads_docstrings_by_sql_filename | — | — |
| tests/tools/test_generate_api_sequences.py::test_function_metadata_reads_docstrings_arguments_and_return_types | — | — |
| tests/tools/test_generate_api_sequences.py::test_function_metadata_requires_docstrings | — | — |
| tests/tools/test_generate_api_sequences.py::test_integration_resources_are_loaded_from_port_directories | — | — |
| tests/tools/test_generate_api_sequences.py::test_ast_helpers_handle_non_matches_and_fallbacks | — | — |
| tests/tools/test_generate_api_sequences.py::test_awaited_api_function_name_rejects_unrelated_awaits | — | — |
| tests/tools/test_generate_api_sequences.py::test_sql_sequence_steps_ignores_missing_or_unparseable_sql | — | — |
| tests/tools/test_generate_api_unit_test_factors.py::test_api_unit_test_factors_from_router_ast | — | — |
| tests/tools/test_generate_api_unit_test_factors.py::test_condition_description_falls_back_to_api_function_docstring | — | — |
| tests/tools/test_generate_api_unit_test_factors.py::test_render_unit_test_markdown_uses_three_sections | — | — |
| tests/tools/test_generate_api_unit_test_factors.py::test_render_implicit_router_errors_section_renders_none | — | — |
| tests/tools/test_generate_db_crud.py::test_operation_label_orders_crud_letters | — | — |
| tests/tools/test_generate_db_crud.py::test_api_name_from_sql_path_uses_api_folder_name | — | — |
| tests/tools/test_generate_db_crud.py::test_api_name_from_sql_path_rejects_non_api_sql_path | — | — |
| tests/tools/test_generate_db_crud.py::test_sql_operations_extracts_crud_from_sqlglot_ast | — | — |
| tests/tools/test_generate_db_crud.py::test_sql_operations_reads_delete_using_tables | — | — |
| tests/tools/test_generate_db_crud.py::test_mutation_target_returns_none_without_target | — | — |
| tests/tools/test_generate_db_crud.py::test_expression_tables_returns_empty_for_non_expression | — | — |
| tests/tools/test_generate_db_crud.py::test_sql_operations_ignores_empty_parsed_statement | — | — |
| tests/tools/test_generate_db_crud.py::test_collect_crud_ignores_tables_not_defined_in_ddl | — | — |
| tests/tools/test_generate_db_crud.py::test_render_csv_outputs_api_rows_and_table_columns | — | — |
| tests/tools/test_generate_db_crud.py::test_csv_escape_quotes_special_values | — | — |
| tests/tools/test_generate_db_crud.py::test_generate_writes_db_crud_csv | — | — |
| tests/tools/test_generate_db_crud.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_parse_reference_target_normalizes_identifier_and_optional_columns | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_parse_relationships_extracts_inline_table_and_alter_foreign_keys | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_relationship_cardinality_uses_nullability_and_uniqueness | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_child_columns_are_unique_supports_composite_table_constraints | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_render_mermaid_includes_tables_keys_and_relationships | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_render_markdown_wraps_mermaid_with_source_ddl_path | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_generate_writes_markdown_or_mermaid_by_output_suffix | — | — |
| tests/tools/test_generate_db_er_diagram.py::test_arg_parser_defaults_format_inference_and_main_output | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_column_extracts_key_nullability_and_reference | — | — |
| tests/tools/test_generate_db_table_specs.py::test_sqlglot_helper_fallbacks | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_column_marks_primary_key_as_unique_and_not_nullable | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_create_table_rejects_non_schema_create | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_tables_supports_comments_and_like_tables | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_tables_supports_commented_out_comment_on_metadata | — | — |
| tests/tools/test_generate_db_table_specs.py::test_parse_tables_raises_for_missing_like_source | — | — |
| tests/tools/test_generate_db_table_specs.py::test_render_table_markdown_includes_columns_constraints_and_escapes_pipe | — | — |
| tests/tools/test_generate_db_table_specs.py::test_generate_writes_sorted_table_specs | — | — |
| tests/tools/test_generate_db_table_specs.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_db_table_specs.py::test_small_helpers | — | — |
| tests/tools/test_generate_e2e_specs.py::test_e2e_flow_steps_cover_generated_api_list | — | — |
| tests/tools/test_generate_e2e_specs.py::test_component_variants_follow_target_coverage_policies | — | — |
| tests/tools/test_generate_e2e_specs.py::test_prerequisites_resolve_dependencies_recursively | — | — |
| tests/tools/test_generate_e2e_specs.py::test_target_cases_skip_embedded_goals_and_carry_matrix_assertions | — | — |
| tests/tools/test_generate_e2e_specs.py::test_e2e_case_list_links_scenarios | — | — |
| tests/tools/test_generate_e2e_specs.py::test_e2e_scenarios_render_steps_settings_and_failure_triggers | — | — |
| tests/tools/test_generate_e2e_specs.py::test_check_e2e_specs_accepts_repository_tree | — | — |
| tests/tools/test_generate_e2e_specs.py::test_check_e2e_specs_reports_missing_generated_case | — | — |
| tests/tools/test_generate_external_crud.py::test_api_name_from_functions_path_uses_api_folder_name | — | — |
| tests/tools/test_generate_external_crud.py::test_api_name_from_functions_path_rejects_non_api_functions_path | — | — |
| tests/tools/test_generate_external_crud.py::test_called_methods_collects_configured_variable_attribute_calls | — | — |
| tests/tools/test_generate_external_crud.py::test_file_operations_maps_service_methods_to_crud_resources | — | — |
| tests/tools/test_generate_external_crud.py::test_file_operations_ignores_unmapped_service_methods | — | — |
| tests/tools/test_generate_external_crud.py::test_collect_service_crud_reads_router_dependencies | — | — |
| tests/tools/test_generate_external_crud.py::test_router_dependency_names_ignores_missing_router | — | — |
| tests/tools/test_generate_external_crud.py::test_generate_writes_requested_external_crud_csvs | — | — |
| tests/tools/test_generate_external_crud.py::test_service_names_for_arg_accepts_all_or_single_service | — | — |
| tests/tools/test_generate_external_crud.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_schema_type_and_constraints | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_enum_comment_descriptions_reads_enum_member_comments | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_parameter_and_request_body_rows | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_auth_header_rows_use_runtime_meaning | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_response_summary_and_render_markdown | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_operation_components_uses_api_specific_error_resource_schema | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_response_description_prefers_status_sample_error_reason | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_empty_and_invalid_sections_render_none | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_render_operation_markdown_handles_missing_description | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_sample_renderers_format_curl_and_json | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_operation_output_path_falls_back_to_default | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_implementation_operation_paths_reads_router_operation_ids | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_operation_samples_are_loaded_from_samples_module | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_module_sample_handles_missing_suffix | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_router_operation_helpers_handle_non_matches | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_iter_operations_and_output_path | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_generate_from_openapi_writes_files | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_openapi_if_specs.py::test_load_fastapi_openapi_returns_schema | — | — |
| tests/tools/test_generate_queries.py::test_name_helpers | — | — |
| tests/tools/test_generate_queries.py::test_type_helpers | — | — |
| tests/tools/test_generate_queries.py::test_placeholder_names_preserves_first_seen_order | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_infers_select_params_and_rows | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_infers_qualified_alias_and_expression_rows | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_marks_null_checked_params_nullable | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_marks_left_join_rows_nullable | — | — |
| tests/tools/test_generate_queries.py::test_operation_from_statements_detects_statement_kind | — | — |
| tests/tools/test_generate_queries.py::test_sql_summary_reads_first_comment_or_falls_back | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_infers_insert_params_and_returning_rows | — | — |
| tests/tools/test_generate_queries.py::test_parse_query_spec_infers_update_params_and_returning_rows | — | — |
| tests/tools/test_generate_queries.py::test_returning_and_mutation_helpers_handle_missing_returning_or_target | — | — |
| tests/tools/test_generate_queries.py::test_collect_param_columns_handles_non_standard_insert_and_update | — | — |
| tests/tools/test_generate_queries.py::test_render_queries_py_includes_required_imports_and_empty_params | — | — |
| tests/tools/test_generate_queries.py::test_render_queries_py_uses_two_blank_lines_between_top_level_blocks | — | — |
| tests/tools/test_generate_queries.py::test_render_queries_py_includes_empty_params_and_date_decimal_imports | — | — |
| tests/tools/test_generate_queries.py::test_render_query_function_uses_fetch_one_for_mutation_returning | — | — |
| tests/tools/test_generate_queries.py::test_render_queries_py_imports_multiple_query_helpers | — | — |
| tests/tools/test_generate_queries.py::test_output_field_falls_back_for_unknown_column_and_plain_expression | — | — |
| tests/tools/test_generate_queries.py::test_infer_row_fields_returns_empty_when_no_select_or_returning | — | — |
| tests/tools/test_generate_queries.py::test_required_imports_handles_minimal_specs | — | — |
| tests/tools/test_generate_queries.py::test_generate_queries_writes_each_api_queries_file | — | — |
| tests/tools/test_generate_queries.py::test_render_compat_queries_py_re_exports_generated_queries | — | — |
| tests/tools/test_generate_queries.py::test_arg_parser_defaults_and_main_output | — | — |
| tests/tools/test_generate_queries.py::test_generate_queries_handles_api_without_sql | — | — |
| tests/tools/test_generate_queries.py::test_unknown_placeholder_type_is_rejected | — | — |
| tests/tools/test_generate_queries.py::test_cast_placeholder_type_is_inferred | — | — |
| tests/tools/test_generate_queries.py::test_comparison_placeholder_can_be_on_left_side | — | — |
| tests/tools/test_generate_query_specs.py::test_sql_tables_and_conditions_preserve_sql_order | — | — |
| tests/tools/test_generate_query_specs.py::test_sql_tables_deduplicates_repeated_tables | — | — |
| tests/tools/test_generate_query_specs.py::test_column_ref_resolution_handles_aliases_and_ambiguity | — | — |
| tests/tools/test_generate_query_specs.py::test_row_column_refs_handles_returning_and_empty_cases | — | — |
| tests/tools/test_generate_query_specs.py::test_param_column_refs_cover_insert_update_and_comparison_paths | — | — |
| tests/tools/test_generate_query_specs.py::test_param_column_refs_falls_back_to_unique_ddl_column | — | — |
| tests/tools/test_generate_query_specs.py::test_parenthesized_condition_items_handles_empty_and_single | — | — |
| tests/tools/test_generate_query_specs.py::test_expression_and_conditions_handle_unaliased_and_empty_paths | — | — |
| tests/tools/test_generate_query_specs.py::test_display_and_render_helpers_cover_empty_and_fallback_paths | — | — |
| tests/tools/test_generate_query_specs.py::test_render_sql_spec_handles_operation_fallback_and_empty_sections | — | — |
| tests/tools/test_generate_query_specs.py::test_render_query_markdown_inserts_blank_line_between_multiple_specs | — | — |
| tests/tools/test_generate_query_specs.py::test_changed_outputs_and_render_changed_cover_missing_and_stale_files | — | — |
| tests/tools/test_generate_query_specs.py::test_generate_query_specs_renders_sql_chapters | — | — |
| tests/tools/test_generate_query_specs.py::test_generate_query_specs_renders_source_tables_and_expanded_aliases | — | — |
| tests/tools/test_generate_query_specs.py::test_generate_query_specs_splits_and_or_conditions | — | — |
| tests/tools/test_generate_query_specs.py::test_render_query_markdown_marks_empty_sections | — | — |
| tests/tools/test_generate_query_specs.py::test_main_writes_outputs_and_check_reports_changed | — | — |
| tests/tools/test_generate_query_specs.py::test_arg_parser_defaults | — | — |
| tests/tools/test_generate_query_specs.py::test_render_query_markdown_handles_no_sql_specs | — | — |
| tests/tools/test_project_guards.py::test_result_identity_and_unexecuted | Given collectorの2件 When 片方だけ成功 Then 他方をnot-runとして残す。 | TECH-QUALITY-AC |
| tests/tools/test_project_guards.py::test_nonpassing_states_preserved | Given 非成功状態 When 変換 Then passedへ変えない。 | TECH-QUALITY-AC |
| tests/tools/test_project_guards.py::test_schema_dictionary_mutations | Given 列辞書欠落・余剰かDDL変更 When schema抽出 Then 不整合拒否か型変化を検出。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_sql_parameter_mutation | Given SQLの束縛変数だけ変更 When 型生成 Then 引数不一致を拒否。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_deterministic_generation | Given 同一source When 2回のクリーン生成 Then byte集合が一致する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_sequence_tracks_conditions | Given 分岐とqueryの順序変更 When AST図生成 Then 図が変化する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_added_api_without_design_update | Given 生成済み設計 When API追加後に設計を更新せず検査 Then 新operationの6帳票欠落とOpenAPI変更を検出する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_unsupported_endpoint_syntax | Given adapterが解析しないtry構文のendpoint When 設計生成 Then 空の成功にせず未対応として拒否する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_sql_target_change_updates_crud | Given 生成済みCRUD When SQLの更新先を変更 Then CRUD model・表・CSVのdriftを検出する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_manual_edit_and_stale_document | Given 生成物の手編集と旧帳票の残存 When drift検査 Then 変更と余剰を報告し既存fileを書き換えない。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_missing_test_for_requirement | Given 受入条件に対応するテスト When テスト削除・タグ欠落・未知タグ Then 要件traceの欠落として拒否する。 | TECH-DESIGN-AC |
| tests/tools/test_project_guards.py::test_missing_collector_result_is_not_run | Given collectorにあるが結果のないcase When 変換 Then not-runとし成功へ数えない。 | TECH-QUALITY-AC |
| tests/tools/test_project_guards.py::test_foreign_run_rejected | Given 別runのcollector原本 When ポータル証跡を構築 Then 混入として拒否する。 | TECH-QUALITY-AC |
| tests/tools/test_project_guards.py::test_publication_allowlist | Given 公開サイトに生ログ・storage state・DB dump When 公開集合を検査 Then 公開を拒否する。 | TECH-PRIVACY-AC |
| tests/tools/test_project_guards.py::test_symlink_not_published | Given 公開サイト内のsymlink When 公開集合を検査 Then 外部fileを公開しない。 | TECH-PRIVACY-AC |
| tests/tools/test_project_migrate.py::test_migrate_and_seed_repeat | Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 | COM-05-AC, COM-02-AC, SLOT-AC16 |
| tests/tools/test_rulecheck_cli.py::test_rulecheck_cli_generate_verify_and_check | — | — |
| tests/tools/test_rulecheck_cli.py::test_metric_exclude_globs_skip_generated_python | — | — |
| tests/tools/test_rulecheck_cli.py::test_endpoint_business_argument_count_excludes_fastapi_depends | — | — |
| tests/tools/test_rulecheck_cli.py::test_additional_metric_checkers_report_failures | — | — |
| vitest::日本時間の入力と次の操作案内 [COM-08-AC] [RULE-04-AC] | 日本時間の入力と次の操作案内 | COM-08-AC, RULE-04-AC |
| vitest::Cognitoのログアウト先 [COM-01-AC] | Cognitoのログアウト先 | COM-01-AC |
| playwright::ログインから予約・履歴・取消・ログアウトまで [COM-01-AC] [SLOT-AC01] [SLOT-02-AC] [SLOT-07-AC] [SLOT-AC04] | ログインから予約・履歴・取消・ログアウトまで | COM-01-AC, SLOT-AC01, SLOT-02-AC, SLOT-07-AC, SLOT-AC04 |
| playwright::一般利用者に資源管理を表示しない [COM-01-AC] [COM-04-AC] | 一般利用者に資源管理を表示しない | COM-01-AC, COM-04-AC |
| playwright::階層検索から設計図とDB探索へ移動する [TECH-PORTAL-AC] | 階層検索から設計図とDB探索へ移動する | TECH-PORTAL-AC |

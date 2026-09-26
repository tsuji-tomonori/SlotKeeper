# テスト設計

| 実在テストID | Given / When / Then | 受入条件 |
| --- | --- | --- |
| backend/tests/test_auth.py::test_bad_claims | Given 不正claim When 業務API呼出し Then 401でDB未接続。 | SLOT-AC14 |
| backend/tests/test_auth.py::test_bad_signature | Given 別の秘密鍵による改ざん When 検証 Then 401。 | SLOT-AC14 |
| backend/tests/test_auth.py::test_anonymous_and_health | Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 | COM-04-AC COM-03-AC |
| backend/tests/test_auth.py::test_user_cannot_create_resource | Given 一般利用者 When 管理API Then 403。 | SLOT-01-AC COM-04-AC |
| backend/tests/test_auth.py::test_cognito_access_and_id | Given Cognito claim When accessとIDを検証 Then accessだけ受理。 | SLOT-AC14 |
| backend/tests/test_domain.py::test_reject_invalid_time | Given 範囲外または刻み不正 When 時刻検証 Then 入力不正。 | SLOT-AC06 RULE-02-AC RULE-03-AC |
| backend/tests/test_domain.py::test_boundaries | Given 15分・4時間・30日境界 When 時刻検証 Then 受け付ける。 | SLOT-AC06 RULE-02-AC RULE-03-AC |
| backend/tests/test_domain.py::test_resource_input | Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 | COM-03-AC RULE-14-AC |
| backend/tests/test_domain.py::test_normalized_input | Given 同じ瞬間のoffset差と前後空白 When 正規化 Then 同一要求。 | SLOT-AC09 |
| backend/tests/test_lambda.py::test_gateway_event | Given HTTP APIイベント When Mangum変換 Then health200・未認証業務401。 | TECH-LAMBDA-AC |
| backend/tests/test_lambda.py::test_distribution_zip | Given 配布ZIP When 隔離pathからimport Then SQLと依存を含むhandlerを読める。 | TECH-LAMBDA-AC |
| backend/tests/test_operations.py::test_request_log_redacts | Given 目的とtokenを含む作成要求 When API呼出し Then 要求ID・operation・status・所要時間だけを記録する。 | COM-07-AC |
| backend/tests/test_operations.py::test_http_status_codes | Given 不正入力・未認証・対象なし・業務競合 When API呼出し Then 422・401・404・409を区別し入力値を反射しない。 | COM-03-AC |
| backend/tests/test_operations.py::test_public_contract_has_no_clock_or_direct_edit | Given 公開OpenAPI When 入力と操作を列挙 Then 現在時刻の上書き入力と予約日時の直接編集がない。 | RULE-04-AC RULE-05-AC |
| backend/tests/test_operations.py::test_missing_targets_return_404 | Given 存在しない予約・資源 When 取消・編集・予約表取得 Then 404で区別する。 | COM-03-AC |
| backend/tests/test_operations.py::test_system_clock_providers | Given 本番の依存 When Clockを取得 Then UTC基準のaware時刻を返し公開入力で置換できない。 | RULE-04-AC |
| backend/tests/test_operations.py::test_transaction_retries_conflicts | Given commit時の直列化競合と一意性競合 When transaction Then 新snapshotで再実行して成功する。 | SLOT-AC03 SLOT-AC07 |
| backend/tests/test_operations.py::test_transaction_limits | Given 解消しない競合と成否不明の切断 When transaction Then 上限後503、再送安全でない処理は再試行しない。 | SLOT-AC12 |
| backend/tests/test_operations.py::test_business_errors_are_not_retried | Given 業務上の重複 When transaction Then 再試行せずそのまま409を返す。 | SLOT-AC02 |
| backend/tests/test_operations.py::test_dsql_connection_uses_official_connector | Given DSQL設定 When 接続 Then 公式connectorへIAM用の接続先・利用者とTLS検証を渡しRepeatable Readにする。 | TECH-DB-AC |
| backend/tests/test_operations.py::test_jwks_client_is_bounded | Given 設定済みJWKS URL When 鍵取得clientを作る Then 短いtimeoutとcache寿命を持つ。 | SLOT-AC14 |
| backend/tests/test_reservations.py::test_create_adjacent_overlap | Given 空き枠 When 作成・重複・隣接 Then 201・409・201。 | SLOT-AC01 SLOT-AC02 RULE-01-AC |
| backend/tests/test_reservations.py::test_privacy_and_cancel | Given Aの予約 When B・Aが詳細取得と取消 Then Bは403で情報非公開、Aは取消。 | SLOT-AC04 SLOT-AC08 SLOT-02-AC RULE-09-AC RULE-13-AC RULE-06-AC COM-04-AC |
| backend/tests/test_reservations.py::test_replay_before_validation | Given 成功後の取消と時刻進行 When 同一キー再送 Then 元の作成応答で履歴は増えない。 | SLOT-AC07 SLOT-AC09 SLOT-AC15 RULE-10-AC |
| backend/tests/test_reservations.py::test_replay_after_start | Given 作成から24時間以内に予約開始 When 再送 Then 時刻違反にせず元応答。 | SLOT-AC15 RULE-11-AC |
| backend/tests/test_reservations.py::test_versions_and_inactive | Given 古い資源版と無効資源 When 更新と作成 Then 409で先行更新維持。 | SLOT-AC05 SLOT-AC11 |
| backend/tests/test_reservations.py::test_future_prevents_disable | Given 将来の確定予約 When 無効化 Then 409。 | SLOT-AC05 RULE-08-AC |
| backend/tests/test_reservations.py::test_cancel_boundaries | Given 確定予約 When 古い版と開始時刻ちょうどの取消 Then 409、履歴1件。 | SLOT-AC11 SLOT-AC13 RULE-13-AC |
| backend/tests/test_reservations.py::test_twenty_concurrent | Given 空き枠と20利用者 When 同時送信 Then 1成功19競合で重複なし。 | SLOT-AC03 |
| backend/tests/test_reservations.py::test_same_key_concurrent | Given 同一キー同一入力 When 20同時再送 Then 同じIDで予約と作成履歴各1件。 | SLOT-AC07 |
| backend/tests/test_reservations.py::test_create_vs_disable | Given 有効資源 When 予約作成と無効化を競合 Then 両方成功しない。 | SLOT-AC10 RULE-08-AC |
| backend/tests/test_reservations.py::test_rollback_at_event | Given 履歴保存の障害 When 作成 Then 予約とキーをrollbackし再送は1件だけ成功。 | SLOT-AC12 RULE-12-AC COM-02-AC |
| backend/tests/test_reservations.py::test_disable_after_start_keeps_record | Given 開始済みの確定予約 When 資源を無効化 Then 無効化でき既存記録を保持し新規予約は拒否する。 | RULE-07-AC |
| backend/tests/test_reservations.py::test_repeatable_read | Given ローカル接続 When 分離レベル取得 Then repeatable read。 | COM-02-AC TECH-DB-AC |
| backend/tests/test_reservations.py::test_list_filters_only_own | Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 | SLOT-AC08 RULE-07-AC |
| backend/tests/test_reservations.py::test_admin_cancels_other_before_start | Given Aの開始前予約 When 管理者が取消 Then 取消と履歴2件、開始後は管理者も拒否。 | SLOT-AC04 SLOT-07-AC RULE-09-AC |
| backend/tests/test_reservations.py::test_cancel_and_rebook_concurrent | Given 確定予約 When 取消と同じ枠の再予約を同時実行 Then 重なる確定予約は最大1件。 | RULE-06-AC |
| backend/tests/test_reservations.py::test_invalid_token_leaves_database | Given 期限切れ・改ざんroleのtoken When 予約作成と資源登録 Then 401/403でDBは変化しない。 | SLOT-AC14 |
| backend/tests/test_reservations.py::test_migrate_and_seed_repeat | Given 既存データ When migrationとseedを繰り返す Then 重複せず既存データを保持する。 | COM-05-AC COM-02-AC SLOT-AC16 |
| backend/tests/test_reservations.py::test_resource_paging_order | Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 | SLOT-01-AC RULE-14-AC |
| infra/tests/test_stack.py::test_serverless_and_authorization | Given 配布ZIP When synth Then 公開bucketと常設サーバーがなく認証と削除保護がある。 | TECH-INFRA-AC |
| infra/tests/test_stack.py::test_routes_are_protected | Given HTTP API When routeを列挙 Then healthだけ認証なしで、他はJWTとaccess scopeが必須。 | TECH-INFRA-AC |
| infra/tests/test_stack.py::test_origin_consistency | Given 環境設定 When synth Then CORS・Cognito callback/logout・API許可元が同じ配信元を指す。 | TECH-INFRA-AC |
| infra/tests/test_stack.py::test_least_privilege_and_private_bucket | Given 合成IAMとbucket policy When 権限を列挙 Then DSQLは対象clusterのDbConnectだけでS3はCloudFrontだけ読める。 | TECH-INFRA-AC |
| infra/tests/test_stack.py::test_environment_settings | Given 環境context When synth Then ログ保持・throttle・環境名が設定どおりで削除保護は共通。 | TECH-INFRA-AC |
| infra/tests/test_stack.py::test_unknown_environment_rejected | Given 未定義や不正な環境名 When 設定を読む Then 推測で合成せず拒否する。 | TECH-INFRA-AC |
| tools/tests/test_guards.py::test_result_identity_and_unexecuted | Given collectorの2件 When 片方だけ成功 Then 他方をnot-runとして残す。 | TECH-QUALITY-AC |
| tools/tests/test_guards.py::test_nonpassing_states_preserved | Given 非成功状態 When 変換 Then passedへ変えない。 | TECH-QUALITY-AC |
| tools/tests/test_guards.py::test_schema_dictionary_mutations | Given 列辞書欠落・余剰かDDL変更 When schema抽出 Then 不整合拒否か型変化を検出。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_sql_parameter_mutation | Given SQLの束縛変数だけ変更 When 型生成 Then 引数不一致を拒否。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_deterministic_generation | Given 同一source When 2回のクリーン生成 Then byte集合が一致する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_sequence_tracks_conditions | Given 分岐とqueryの順序変更 When AST図生成 Then 図が変化する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_added_api_without_design_update | Given 生成済み設計 When API追加後に設計を更新せず検査 Then 新operationの6帳票欠落とOpenAPI変更を検出する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_unsupported_endpoint_syntax | Given adapterが解析しないtry構文のendpoint When 設計生成 Then 空の成功にせず未対応として拒否する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_sql_target_change_updates_crud | Given 生成済みCRUD When SQLの更新先を変更 Then CRUD model・表・CSVのdriftを検出する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_manual_edit_and_stale_document | Given 生成物の手編集と旧帳票の残存 When drift検査 Then 変更と余剰を報告し既存fileを書き換えない。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_missing_test_for_requirement | Given 受入条件に対応するテスト When テスト削除・タグ欠落・未知タグ Then 要件traceの欠落として拒否する。 | TECH-DESIGN-AC |
| tools/tests/test_guards.py::test_missing_collector_result_is_not_run | Given collectorにあるが結果のないcase When 変換 Then not-runとし成功へ数えない。 | TECH-QUALITY-AC |
| tools/tests/test_guards.py::test_foreign_run_rejected | Given 別runのcollector原本 When ポータル証跡を構築 Then 混入として拒否する。 | TECH-QUALITY-AC |
| tools/tests/test_guards.py::test_publication_allowlist | Given 公開サイトに生ログ・storage state・DB dump When 公開集合を検査 Then 公開を拒否する。 | TECH-PRIVACY-AC |
| tools/tests/test_guards.py::test_symlink_not_published | Given 公開サイト内のsymlink When 公開集合を検査 Then 外部fileを公開しない。 | TECH-PRIVACY-AC |
| vitest::日本時間の入力と次の操作案内 [COM-08-AC] [RULE-04-AC] | 日本時間の入力と次の操作案内 | COM-08-AC RULE-04-AC |
| vitest::Cognitoのログアウト先 [COM-01-AC] | Cognitoのログアウト先 | COM-01-AC |
| playwright::ログインから予約・履歴・取消・ログアウトまで [COM-01-AC] [SLOT-AC01] [SLOT-02-AC] [SLOT-07-AC] [SLOT-AC04] | ログインから予約・履歴・取消・ログアウトまで | COM-01-AC SLOT-AC01 SLOT-02-AC SLOT-07-AC SLOT-AC04 |
| playwright::一般利用者に資源管理を表示しない [COM-01-AC] [COM-04-AC] | 一般利用者に資源管理を表示しない | COM-01-AC COM-04-AC |
| portal::階層検索から設計図とDB探索へ移動する [TECH-PORTAL-AC] | 階層検索から設計図とDB探索へ移動する | TECH-PORTAL-AC |

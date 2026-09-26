# 参照tools全件対応表（自動生成）

直接編集せず reference_inventory.py で再生成する。

参照: https://github.com/tsuji-tomonori/lazunex / `096e1e580ab1c0670c57e4febad2bd9fdd4698ee` / 52 files

採用区分は導入先での実装方針。reference-blueprintは導入先への実接続済みを意味しない。

| パス / blob SHA | 用途 / 分類 | 要件ID | 採用区分 / 理由 | 固有前提 | 接続先 |
|---|---|---|---|---|---|
| src/tools/__init__.py<br>baa82b690b569cc06871fecc9a7322c1387cb601 | tool packageの識別<br>package-support | REQ-ASBUILT-030 | not-adopted<br>Python package markerは導入先言語のmodule方式に依存し、検査能力を持たない。 | Python runtime | 非採用 |
| src/tools/check_api_contracts.py<br>e6404011ff796f20701b2205ebd3880fb80cd961 | 操作metadataと登録operationの対応検査<br>static-checker | REQ-ASBUILT-012, REQ-DESIGN-009 | adapt<br>metadataの実登録照合を基に、導入先の公開契約と責務の実呼出しを検査する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_descriptions.py<br>54f3e3c888862da3b2fb0f89ef7698f7f3684377 | API/schema/enumの日本語説明検査<br>static-checker | REQ-DOCS-002 | adapt<br>Field/decorator依存を導入先の型・公開metadataへ置換し、指定された説明言語を検査する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_exception_summaries.py<br>7dad75b7d658b26a37da4c5bb7c024782e8e79ac | 個別処理・外部依存の例外summary検査<br>static-checker | REQ-ASBUILT-027 | extend<br>例外summary検査を基に、捕捉/再送出から応答・運用対応までの未解決経路も検出する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_function_exception_policy.py<br>939adc54d590b47ec8c2ed4b622021d7bc89ea6d | 個別業務処理のHTTP例外禁止と資源未設定時の例外方針検査<br>static-checker | REQ-DESIGN-021 | adapt<br>HTTPExceptionの直接送出禁止を通信層固有例外の境界へ適応する。固有資源名・例外型を固定せず、別名・同期/非同期の正負例を追加する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_function_names.py<br>67081d8a0728e8d703199810b6594b297b310ce3 | 処理名の動詞・対象・条件辞書との照合<br>static-checker | REQ-DOCS-002 | not-adopted<br>lazunex固有の命名辞書は移植しない。責務と自然言語説明の検査で可読性を確保する。 | Python AST | 非採用 |
| src/tools/check_api_function_resource_usage.py<br>8c5f4e7971450d57d8dabc8ee10ccbcb04b21d8c | 個別処理のDB/外部port利用と資源引数検査<br>static-checker | REQ-DESIGN-011 | adapt<br>resource-free例外とport識別を導入先へ適応し、実I/O利用を検証する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_function_tests.py<br>191508856e6b01f417fdfe63509e833f6b49206f | 個別処理と実test参照の対応検査<br>static-checker | REQ-ASBUILT-020 | extend<br>名前参照だけで充足とせず、実collector IDと要件・処理の明示traceを照合する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_managed_literals.py<br>1a1e106bcb0a708bfd3427168d9a8bec8cf7f3b4 | 業務literalの定数・enum利用検査<br>static-checker | REQ-ASBUILT-030 | not-adopted<br>lazunex業務定数は対象固有であり移植しない。endpoint許可symbol制約は別途全source走査で実装する。 | Python AST | 非採用 |
| src/tools/check_api_mermaid_sequences.py<br>22e24c73be054e25ce93c4e99c2d98a18bc02908 | Mermaidのparticipantとラベル形式検査<br>static-checker | REQ-ASBUILT-026 | adapt<br>Mermaid表現検査を再利用し、実call graphとの対応は導入先解析器が補う。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_router_ignored_returns.py<br>1614ef6366a846aff222223afdfecbe222c3ac8c | 意味ある処理戻り値の破棄と副作用検査<br>static-checker | REQ-DESIGN-018 | extend<br>await式中心の検査を同期/非同期・別名呼出しの負例へ拡張する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_router_logging_tests.py<br>ad01c72af11b1c3947271dec2f0915a664c6aab5 | API異常ログの実HTTP sample assertion検査<br>static-checker | REQ-ASBUILT-013, REQ-ASBUILT-027 | adapt<br>logger wrapper/test helper固有の名前を実呼出しとassertionの対応へ適応する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_router_test_asserts.py<br>e3199682adefde060eddf2eb9e97eb096cfa9f29 | sample応答とCRUD対象DB状態のassert検査<br>static-checker | REQ-ASBUILT-013, REQ-ASBUILT-014 | extend<br>source文字列照合から導入先の実テスト検証へ強化し、非SQL副作用も含める。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_router_tests.py<br>89e4f0cfda8cc9e098640959bd635b34fbbf39a7 | 各operationの対応router test存在検査<br>static-checker | REQ-ASBUILT-020 | extend<br>ファイル名一致だけでなく実collectorの検証単位を照合する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_router_unit_test_factors.py<br>fc5ed4c2abdc0cf9b319e88eaf089a779977f830 | 要因ケースとHTTP/status/log assertion検査<br>static-checker | REQ-ASBUILT-022, REQ-ASBUILT-028 | adapt<br>pytest固有nodeとassert構造を導入先のcollectorと自然言語GWTへ対応させる。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_sequence_success_responses.py<br>585661317653b57073b805b6be2ac250bde3fbe5 | sequenceの成功応答の存在・配置検査<br>static-checker | REQ-ASBUILT-026 | extend<br>2xx文字列だけに頼らず、実フローの成功・内部失敗継続・例外を検査する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_sql_ddl_usage.py<br>3605134ca374cc1c3dbe06ad9c3c9933bbe8f1b7 | SQLのtable/column参照とDDL定義の整合検査<br>static-checker | REQ-DESIGN-004, REQ-DESIGN-012, REQ-DESIGN-017 | adapt<br>SQL dialectと型情報を導入先parserへ合わせ、未対応構文は未検証として残す。 | Python runtime, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_api_status_samples.py<br>5672da8d5a6df21ad2f9446053196403a546f84c | 実route/OpenAPI/sampleのstatusと型の整合検査<br>static-checker | REQ-ASBUILT-012, REQ-ASBUILT-013 | adapt<br>FastAPI/Pydanticの実ロードを導入先の実公開契約exportとsample実行へ置換する。 | Python AST, FastAPI, Pydantic | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_bool_router_conditions.py<br>313614e2c288b1a19b619c6795d09a05e541bd3f | 真偽戻り値の条件式利用検査<br>static-checker | REQ-DESIGN-018 | adapt<br>真偽値の条件利用を戻り値の実利用検査へ適応し、同期/非同期・別名呼出しの単独破棄を拒否する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_constant_bool_returns.py<br>fa4bc35cfea7637ea256448f8502c6061b3335ca | 定数boolしか返さない判定処理の検査<br>static-checker | REQ-DESIGN-019 | adapt<br>型付き処理の戻り値を導入先の同期/非同期構造で検査する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_e2e_case_evidences.py<br>b1ac9b25409cd500ce0df429b66c1f836218fb6d | E2EケースとGWT証跡binding検査<br>e2e | REQ-EVIDENCE-002 | adapt<br>YAML binding方式と業務ケースIDを導入先の実E2E evidenceへ対応させる。 | Python runtime, YAML / PyYAML | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_e2e_specs.py<br>d76facf07ddfc0f3bd199726d070c7c989611746 | E2E構成・依存・索引・coverage契約検査<br>e2e | REQ-ASBUILT-008, REQ-EVIDENCE-002 | adapt<br>固定flowとcomponent数量を持ち込まず、導入先実inventoryとの集合一致にする。 | Python runtime, YAML / PyYAML | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_exception_router_handlers.py<br>20a4218829e919e9481d065fa6a749c31aef9d26 | 例外を生じる個別処理呼出しの捕捉境界検査<br>static-checker | REQ-ASBUILT-027, REQ-DESIGN-011 | extend<br>try包含判定を基に再送出・内部捕捉・応答変換までの経路を追跡する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_operational_logging.py<br>85cf26905cbac5a504cad9ba9ccdc7aa28cda396 | 運用logger規約の書換えなし検査入口<br>static-checker | REQ-ASBUILT-027, REQ-DESIGN-013 | adapt<br>catalog検証の再利用という構造を採用し、ログprivacyと安全な型を導入先で検証する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/check_router_error_response_returns.py<br>19702b24ee37c05b5a60d9530da07998a88d75ee | endpointの宣言エラーstatusと実returnの集合検査<br>static-checker | REQ-ASBUILT-027, REQ-ASBUILT-033 | extend<br>正常status内失敗と動的応答を追跡し、未解決を一律500へ変換しない。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/e2e_models.py<br>d75e3dc2796a61cb579be8087ed9e294edf66a91 | E2Eの対象・部品・組合せ・実行assertionモデル<br>e2e | REQ-ASBUILT-008 | adapt<br>モデル形を参考にし、固定の事業flowと対象定数は導入先実装から置換する。 | Python runtime, YAML / PyYAML | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_api_detail_design.py<br>3f607c3d2e952431cfe0165125167534ea52cac7 | 入力・前提・資源変更・応答取得元の詳細設計生成<br>as-built-generator | REQ-ASBUILT-004, REQ-ASBUILT-023 | adapt<br>型・SQL・応答組立の抽出を導入先言語で実装し、章順を構成profileで共有する。 | Python AST, FastAPI, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_api_list.py<br>2a78a6fee04dff1b05ceb052815c49064cd975b5 | export済みAPI集合から索引生成<br>as-built-generator | REQ-ASBUILT-005, REQ-ASBUILT-025 | adapt<br>実operation登録集合からグループ/API索引と帳票を生成する。 | Python runtime, FastAPI | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_api_message_catalog.py<br>a0305f66432c7394817fffa066bf331952bb0ba4 | 運用logger呼出し・型付きcontext・message帳票生成<br>as-built-generator | REQ-ASBUILT-027, REQ-DESIGN-013 | extend<br>wrapper静的解析を基に例外/HTTP対応とprivacy負例を導入先で補強する。 | Python AST, Pydantic | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_api_pytest_cases.py<br>b80802a383700d42a7446840cbdf0346eb8c36e9 | 帳票ケースからpytest雛形生成<br>as-built-generator | REQ-ASBUILT-028 | not-adopted<br>生成雛形は実行テストと自然言語GWTの代替にならない。導入先で実テストを作成する。 | Python runtime, pytest | 非採用 |
| src/tools/generate_api_sequences.py<br>f926e654d6dff047cb4a5b9c1153477d9042255e | endpoint処理順・条件・例外・transactionのsequence生成<br>as-built-generator | REQ-DESIGN-002, REQ-ASBUILT-026 | extend<br>命名推測やframework定型補完を成功根拠とせず、実call graphと未対応診断を導入先で実装する。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_api_unit_test_factors.py<br>d25b27db23552370d9730d2ccee39629bd62113b | 分岐/例外の要因・組合せ・詳細帳票生成<br>as-built-generator | REQ-ASBUILT-022, REQ-ASBUILT-028 | extend<br>直積を無条件生成せず到達性を考慮し、実検証単位のGWTを対応させる。 | Python AST, FastAPI, Pydantic | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_db_crud.py<br>d467c6d69b12db141f2a71c885f8a8ceac156662 | SQL正本からAPI×table CRUD CSV生成<br>as-built-generator | REQ-ASBUILT-006, REQ-ASBUILT-024 | extend<br>参照先と変更先の区別を基に実到達call graph・アクセスなし・同一モデル表/図/根拠を追加する。 | Python runtime, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_db_er_diagram.py<br>0a374040b466eda429db9e51a04bb70abbc8f353 | DDLの参照制約・多重度からER生成<br>as-built-generator | REQ-ASBUILT-007 | adapt<br>DDL parserとdialectを導入先へ置換し、未解決の関係を推測しない。 | Python runtime, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_db_table_specs.py<br>80369de8e65bacd3e5239db04eef959267e12346 | DDLからtable/column/制約の帳票生成<br>as-built-generator | REQ-ASBUILT-007 | adapt<br>SQL採用時だけ対象dialectの構造解析から生成する。 | Python runtime, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_e2e_case_list.py<br>a20fad9069f57a871d7c446dbcb0852d06e0d7c4 | E2Eケース一覧・対象matrix・除外CSV生成<br>e2e | REQ-ASBUILT-008, REQ-EVIDENCE-002 | adapt<br>lazunex固有variant/flow定数を移植せず実collector/シナリオの対象へ対応させる。 | Python runtime, YAML / PyYAML | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_e2e_scenarios.py<br>efd66df8dae722c2764b13169641eb80fd0da6d4 | E2Eの前提・操作・期待結果・証跡詳細生成<br>e2e | REQ-ASBUILT-008 | adapt<br>YAMLと業務flow固有の導出を導入先のテスト情報へ適応する。 | Python runtime, YAML / PyYAML | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_external_crud.py<br>9d355a503c12b92f5939125a29b99dc9b07b62d6 | 外部サービス呼出しから資源別CRUD CSV生成<br>as-built-generator | REQ-ASBUILT-006, REQ-ASBUILT-024 | extend<br>固定service/method辞書を導入先portへ対応させ、未知呼出しをアクセスなしにしない。 | Python AST | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_openapi_if_specs.py<br>04a3daa2b71173fbbb7bc5253efaf473078ef65e | 実OpenAPIと型・sampleからinterface帳票生成<br>as-built-generator | REQ-DESIGN-003, REQ-ASBUILT-022 | adapt<br>FastAPI app起動を導入先の公開interface exportへ置換する。 | Python AST, FastAPI | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_queries.py<br>f91b36d78b649e6acaf453589a5e9956db70a91c | SQL束縛引数・投影型・実行wrapper生成<br>as-built-generator | REQ-DESIGN-007, REQ-DESIGN-012, REQ-DESIGN-017 | adapt<br>SQLAlchemy/Pydanticと型推定を導入先の型/DB portへ適応し、厳格Paramsと投影/NULL対応を検査する。 | Python runtime, Pydantic, SQL dialect / sqlglot, SQLAlchemy | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generate_query_specs.py<br>439c3f6c80717947fb74be82d62199bedcbb0eea | SQLごとの種別・表・型・条件の帳票生成<br>as-built-generator | REQ-DESIGN-004, REQ-ASBUILT-023 | adapt<br>SQL構造情報を導入先parserから取得し、名前に所有先を含め衝突を拒否する。 | Python runtime, SQL dialect / sqlglot | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/generation_io.py<br>c3356cd1846353574ad3de536c47db9a6a00f36b | 生成fileの差分比較と書込み共通化<br>common-io | REQ-ASBUILT-001, REQ-ASBUILT-002, REQ-ASBUILT-035 | extend<br>共通IOを基に所有root・symlink・旧出力・byte一致検査を追加する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/__init__.py<br>99208b61f9a7374accb96d46e125671329473d4f | rule engine package marker<br>rule-engine | REQ-ASBUILT-030 | not-adopted<br>Python package構造だけで検査能力がなく、導入先のmodule方式へ委ねる。 | Python runtime | 非採用 |
| src/tools/rulecheck/__main__.py<br>eb53e2f31b2f703ad32ef64b8a41faa3e7d18e08 | rule engine CLI転送entrypoint<br>rule-engine | REQ-ASBUILT-030 | not-adopted<br>Python -m用の起動転送は導入先CLIへ委ねる。 | Python runtime | 非採用 |
| src/tools/rulecheck/builtin_checks.py<br>18bd805d125ac355917168e5ee1ceedd28f05b61 | 配置・依存・flow・定量条件のchecker登録集合<br>rule-engine | REQ-DESIGN-008, REQ-DESIGN-009, REQ-DESIGN-010, REQ-DESIGN-014, REQ-DESIGN-015, REQ-DESIGN-016, REQ-DESIGN-011, REQ-DESIGN-020, REQ-DESIGN-021, REQ-DESIGN-022 | extend<br>配置・依存・flowに加えrouter_error_handling、functions_exception_policy、functions_public_contractを適応する。包括的捕捉・業務層の通信例外・説明欠落を検査し、別名/相対参照・非公開処理も選択profileに沿って拡張する。固有path・命名・固定数量閾値は移植しない。 | Python AST, FastAPI, SQLAlchemy | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/checklist.py<br>68131acf65ecb8294383d26712324936a40e6392 | 規約checker項目の一覧埋込み生成と差分検査<br>rule-engine | REQ-ASBUILT-017 | not-adopted<br>Markdown規約を第二正本にしない。Quint正本の要件IDと導入先check対応を使う。 | Python runtime | 非採用 |
| src/tools/rulecheck/cli.py<br>bbc409a99ed90f86d1ec577ead31d2a357f83a78 | 生成・検証・評価のCLI統合<br>rule-engine | REQ-ASBUILT-002, REQ-ASBUILT-031 | adapt<br>既存target-owned入口に接続し、構成適合/drift/test/未検証を別結果として返す。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/config.py<br>3a03ae43e1e35d330e88a6ff20744b72242f70b5 | 既定規約設定とoverrideの結合<br>rule-engine | REQ-ASBUILT-017 | adapt<br>固定のlazunex閾値は持ち込まず、導入先で採用した設定と要件を照合する。 | Python runtime, pytest | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/evaluator.py<br>b977822f4f5a07710bce0cb44bec815f2d6ba8a9 | checker dispatchと例外/未知checkの失敗集約<br>rule-engine | REQ-ASBUILT-032 | adapt<br>未知checkerや検査例外を成功にしない評価方式を導入先入口へ接続する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/models.py<br>a23c247046565bcfd203a2f2a3bc4f3ee913da12 | Rule/CheckContext/CheckResultの共通型<br>rule-engine | REQ-ASBUILT-031 | adapt<br>Python dataclassを導入先の型へ置換し、4種類の報告と根拠を分離する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/report.py<br>2e806069711745923f82e6584cf4bd3d5542f15e | checker結果の集計とMarkdown整形<br>rule-engine | REQ-ASBUILT-019, REQ-ASBUILT-031 | adapt<br>pass/fail/manual/skipの区別を保持して導入先の既存エビデンスに接続する。 | Python runtime | .agents/skills/generate-implementation-design/references/adapter-contract.md |
| src/tools/rulecheck/rule_parser.py<br>2d8dbd62335a1105a5cefee21da88f7920ce4092 | Markdown規範行とchecker tagの抽出<br>rule-engine | REQ-ASBUILT-017 | not-adopted<br>規範Markdownのparseで要件正本を二重化せず、Quint派生JSONを読む。 | Python runtime | 非採用 |

## 参照toolsだけでは満たせない要件

| 要件ID | 不足と導入先で必要な実装 |
|---|---|
| REQ-ASBUILT-003 | 出力隔離と直接編集禁止bannerは導入先の所有rootに合わせて実装する。 |
| REQ-ASBUILT-009 | 参照toolは実test結果JSONの公開安全な参照viewを完結しない。導入先collectorとportalを接続する。 |
| REQ-ASBUILT-010 | tool自身のCLI/flow設計の抽出器はこの52filesに見当たらず導入先で追加する。 |
| REQ-ASBUILT-011 | catalog全体一意のerror IDと全error branch集合の一致は導入先adapterで補う。 |
| REQ-ASBUILT-015 | テスト構造の意味を導入先collector/解析器で検査し、雛形生成を成功としない。 |
| REQ-ASBUILT-016 | coverage実測の分母分子・採用目標との照合は導入先coverage collectorで補う。 |
| REQ-ASBUILT-018 | 抑制理由・孤児・反復の監査一覧は導入先linterと抑制設定から生成する。 |
| REQ-ASBUILT-021 | API/data/infra/frontend全領域の接続判定はadapter manifestで補う。 |
| REQ-ASBUILT-024 | CSV・表・図・抽出根拠の単一モデル一致と未解決呼出しの失敗扱いは参照実装から拡張が必要。 |
| REQ-ASBUILT-029 | 言語非依存manifest schemaと要件集合照合は共通check_designで新設する。 |
| REQ-ASBUILT-034 | 参照集合の欠落・余剰・blob SHA再照合はreference_inventoryで新設する。 |
| REQ-ASBUILT-035 | generation_ioは渡された生成対象だけを比較・書込みする。旧対象残存の拒否と所有出力を毎回空にする二重生成は共通check_designで補う。 |
| REQ-DESIGN-001 | 1 operation単位の責務分割を実source集合と照合するadapterを導入先で実装する。 |
| REQ-DESIGN-005 | この参照toolsはinfra全体の生成器を提供しない。導入先の構築artifactから生成する。 |
| REQ-DESIGN-006 | 導入先generatorの非破壊checkと共通二重生成を接続する。 |
| REQ-DESIGN-009 | 参照の配置・metadata検査だけではendpointの応答builder実呼出し、未参照contract/sample、空責務、旧集約への単純委譲を網羅しない。導入先で実call/参照を照合する。 |
| REQ-DESIGN-014 | 全endpoint sourceの非endpoint補助関数・入れ子・class/method・lambda・未登録endpointを一律拒否する検査は参照52filesでは確認できない。利用者指定profileの追加checkerとして導入先で実装する。 |
| REQ-DESIGN-015 | 参照のimport文字列中心の検査を拡張し、別名・相対importを実所有先へ解決してAPI間直接依存を拒否する。解決不能を依存なしとしない。 |
| REQ-DESIGN-018 | await中心の参照checkerを同期/非同期の実体・戻り契約・別名呼出しへ拡張する。値なしの検証専用処理は実体照合を維持する。 |
| REQ-DESIGN-020 | 参照のgeneric例外名検査を、型指定なし・別名・集合に隠れた包括的捕捉まで拡張する。対象言語の例外階層と宣言済み集合を解決する。 |
| REQ-DESIGN-022 | 参照の公開関数docstring検査を選択profileの全対象処理へ適応する。空説明を拒否し、日本語既定と実責務への対応は導入先で確認する。 |
| REQ-DESIGN-023 | 個別処理からendpoint/worker共有workflowへの逆依存を一律に拒否する能力は参照toolsだけでは完結しない。別名/相対参照・同期/非同期の正負例と共有workflowの設計追跡を導入先で追加する。 |
| REQ-DESIGN-024 | 固定参照の構成粒度・責務・例外/logger/query型/帳票の意味と適用外を導入先要件・版付きprofileへ記録する能力は、全件tool棚卸しに加えて導入先で接続する。 |
| REQ-DESIGN-025 | 配置変更前後のHTTP・transaction・外部呼出し前後の認可・実保存先回帰・既存E2E・証跡閲覧は導入先の同一revisionの実行テストへ接続する。参照repositoryの検査を導入先成功の証拠としない。 |
| REQ-DOCS-001 | 人向け説明の意味的可読性は対象言語と要求言語に基づきレビューで補う。 |
| REQ-EVIDENCE-001 | 初期品質portalのcollector/framework接続と公開準備は導入先で実装する。 |
| REQ-EVIDENCE-003 | revision/run・allowlist・公開権限は既存evidence guardrailと導入先collectorで補う。 |
| REQ-EVIDENCE-004 | 階層検索・現在位置・CSVのブラウザE2Eは共通portalで追加する。 |

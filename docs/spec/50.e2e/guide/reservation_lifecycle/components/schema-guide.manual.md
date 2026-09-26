# components YAML schema guide

## 対象ファイル

- `components/<component>/component.manual.yaml`
- `components/<component>/actions.manual.yaml`
- `components/<component>/states.manual.yaml`
- `components/<component>/data.manual.yaml`
- `components/<component>/evidences.manual.yaml`
- `components/<component>/bindings.manual.yaml`

## 役割

component coverage の中心になる定義群。component の責務、操作、状態、入力データ、証明すべきエビデンス、step/evidence binding をまとめる。`src/tools/e2e_models.py` は action/state/data の互換条件から component variant を生成する。

## `component.manual.yaml`

component 自体の責務 `purpose`、関係する `aggregate`、守るべき `business_invariants`、主対象 `targets.primary` を書く。不変条件はケース一覧の「コンポーネントごとの要素」に出る。

## `actions.manual.yaml`

| フィールド | 内容 |
|---|---|
| `id` | action ID。variant ID の action 部分になる。 |
| `title` | ケース一覧とシナリオに出す表示名。 |
| `operation_type` | `command`, `query`, `side_effect`, `evidence` のいずれか。 |
| `default_result` | 代表成功 state。 |
| `target` | `member`、`resource`、その配列、または空配列。 |
| `compatible_states` | 組み合わせ可能な state ID。 |
| `requires` | 実行前に必要な状態。レビュー用の明示情報。生成で使う依存は `flow.manual.yaml` の `component_dependencies` に書く。 |
| `case_generation` | goal case 化の制御。`as_goal: true`、または `standalone_cases` に state/data の組を書く。query/evidence では明示しない限り goal にならない。 |

## `states.manual.yaml`

| フィールド | 内容 |
|---|---|
| `continue_flow` | `false` の失敗系は既定で代表 target だけを生成する。 |
| `target_coverage` | `all`、`canonical_pair`、`canonical_member`、`canonical_resource`。data/action より優先する。 |
| `compatible_actions` | 組み合わせ可能な action。 |
| `requires_data_tags` | この state に使える data profile の tag。 |
| `provides.variables` | 後続 step が使う capture 名。 |

## `data.manual.yaml`

| フィールド | 内容 |
|---|---|
| `title` | data profile 名。 |
| `display_title` | ケース一覧の要素表に出す名前。省略時は `title`。 |
| `label` | 具体データ名の接尾辞。`Member A x Room A の予約` のように対象名へ連結する。 |
| `label_mode` | `target` の場合、具体データ名を対象名だけにする。 |
| `coverage_role` | `canonical_success`、`negative`、`evidence_probe`。`evidence_probe` は standalone case 指定がある場合だけ goal になる。 |
| `compatible_actions` / `compatible_states` | 組み合わせ可能な action/state。 |
| `target_coverage` | target 展開の既定値。 |
| `tags` | binding と state の互換判定に使う。 |
| `request` / `expected` | シナリオの「設定値」表へ平坦化して出す。 |

## `evidences.manual.yaml`

`collector.step` に `steps/<group>/*.step.manual.yaml` または `manual_log_query` を書く。`ok_condition` と `save_as` は placeholder を展開してシナリオへ出す。`save_as` は `${case.id}_E_` で始める。

## `bindings.manual.yaml`

| フィールド | 内容 |
|---|---|
| `when` | action、state、`data_tags.include` の一致条件。 |
| `steps` | 実行する step YAML。 |
| `evidences` | この variant が証明する evidence ID。 |
| `failure_trigger` | 失敗系を発生させる手順。シナリオに「失敗を発生させるため、…」として出る。 |
| `procedure` | 正常系の実行条件。シナリオに「実行条件として、…」として出る。 |
| `error_settings` | 失敗系の追加設定。設定値表へ `error.*` として出る。 |

`check_e2e_case_evidences` は、すべてのケースの selected variant に binding と既知 evidence があることを検査する。

# rules YAML schema guide

## 対象ファイル

- `rules/matrix.manual.yaml`
- `rules/pruning.manual.yaml`
- `rules/renderer.manual.yaml`

## 役割

variant/case 生成、枝刈り、Markdown レンダリングの方針をレビュー可能な形で残す。生成器の実際の展開規則は `flow.manual.yaml` と component YAML から決まり、rules は方針の宣言と検査対象を持つ。

## `matrix.manual.yaml`

| キー | 内容 |
|---|---|
| `variant_generation` | 互換判定、data policy、target policy。 |
| `component_variant_generation.dimensions` | component ごとの展開軸。`component_sequence` の全 component を列挙する。 |
| `component_case_generation.strategies` | `component_variant_coverage` と `interaction_coverage` を必須とする。 |
| `coverage_assertions` | `every_variant_has_case` と `every_target_has_case` を必須とする。 |

## `pruning.manual.yaml`

`component_pruning` に枝刈り方針、`state_rules` に state 到達後に除外する component/action を書く。ケース一覧の「枝刈り規則」表は `flow.manual.yaml` の `case_list_rules` から生成する。

## `renderer.manual.yaml`

ケース Markdown の出力先、ファイル名、セクション、エビデンス/step 番号の付け方を宣言する。

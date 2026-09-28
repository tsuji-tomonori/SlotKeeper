# reservation_lifecycle E2E YAML overview

## 目的

このドキュメントは `docs/spec/50.e2e/reservation_lifecycle/` 配下の E2E 仕様 YAML の全体像を示す。各フォルダの YAML schema と記載方針は、`docs/spec/50.e2e/guide/reservation_lifecycle/` 配下の各 `schema-guide.manual.md` を参照する。

E2E 仕様は JSON Schema ではなく、`src/tools/e2e_models.py`、`src/tools/generate_e2e_case_list.py`、`src/tools/generate_e2e_scenarios.py`、`src/tools/check_e2e_specs.py` が読む YAML shape として管理する。lazunex では対象軸（Project/API）、既定前提variant、失敗の起こし方をPythonに直書きしていたが、SlotKeeperではそれらを `flow.manual.yaml` と component YAML に宣言し、生成器はYAMLだけから決定的にケースを組み立てる。

## ディレクトリ構成

```text
docs/spec/50.e2e/
|-- guide/
|   `-- reservation_lifecycle/
|       |-- overview.manual.md
|       |-- targets/schema-guide.manual.md
|       |-- components/schema-guide.manual.md
|       |-- steps/schema-guide.manual.md
|       |-- templates/schema-guide.manual.md
|       `-- rules/schema-guide.manual.md
`-- reservation_lifecycle/
    |-- flow.manual.yaml
    |-- case-list_gen.md
    |-- case-variant-index_gen.md
    |-- pruned-cases_gen.csv
    |-- targets/
    |   |-- members/*.target.manual.yaml
    |   `-- resources/*.target.manual.yaml
    |-- components/
    |   `-- <component>/
    |       |-- component.manual.yaml
    |       |-- actions.manual.yaml
    |       |-- states.manual.yaml
    |       |-- data.manual.yaml
    |       |-- evidences.manual.yaml
    |       `-- bindings.manual.yaml
    |-- steps/<group>/*.step.manual.yaml
    |-- templates/steps/*.manual.yaml
    |-- rules/*.manual.yaml
    `-- cases/*.gen.md
```

## 役割

| パス | 役割 | 主な利用元 |
|---|---|---|
| `flow.manual.yaml` | E2E フロー全体、対象軸、API step、依存関係、matrix、case policy を定義する。 | `e2e_models`, `check_e2e_specs` |
| `targets/` | E2E で使う Member/Resource の論理対象と既定値を定義する。 | `e2e_models`, `generate_e2e_scenarios` |
| `components/` | component 単位の操作、状態、データ、エビデンス、binding を定義する。 | `e2e_models`, `generate_e2e_case_list`, `generate_e2e_scenarios`, `check_e2e_case_evidences` |
| `steps/` | シナリオに出す step 仕様を定義する。 | `generate_e2e_scenarios`, `check_e2e_specs` |
| `templates/` | API 呼び出し template を定義する。参照する sample は実装の `samples.py` を指す。 | `check_e2e_specs` |
| `rules/` | variant/case 生成、枝刈り、Markdown レンダリング方針を定義する。 | `check_e2e_specs`, reviewer |
| `case-list_gen.md`, `case-variant-index_gen.md`, `cases/*.gen.md`, `pruned-cases_gen.csv` | 生成物。手編集しない。 | reviewer |

## 共通ルール

すべての手動 YAML は先頭に `schema_version: 1` を置く。component/action/state/data/evidence は snake_case、Member target は `member_A` 形式、Resource target は `room_A` / `equipment_A` 形式を使う。

placeholder は実値ではなく参照値を書く。代表例は `${case.id}`、`${member.id}`、`${member.title}`、`${resource.id}`、`${resource.title}`、`${resource.defaults.name}`、`${admin_token}`、`${member_token}`、`${env.E2E_BOOKING_DATE}`。access token の実値は YAML、Markdown、ログに書かない。

component variant ID は `flow.manual.yaml` の `target_dimensions` の順で対象を並べて組み立てる。

```text
<component>.<action>[.<member>][.<resource>].<state>@<data>
```

例:

```text
resource_catalog.register_resource.room_A.registered@resource_default
reservation_booking.book_slot.member_A.room_A.booked@booking_default
```

## `flow.manual.yaml`

| キー | 内容 |
|---|---|
| `flow` | flow ID、表示名、説明。 |
| `target_dimensions` | 対象軸。`id`、表示名、`targets/<directory>/`、代表target `canonical`、target ID一覧。 |
| `steps` | API step。`operation_id`、HTTP method/path、template、capture 名。 |
| `component_sequence` | ケース一覧と CSV の component 列順。 |
| `default_variants` | 依存解決で使う component ごとの既定 action/state/data。 |
| `embedded_goals` | 後続ケースの前提として検証するため単独 goal case にしない variant。 |
| `component_dependencies` | goal variant の前提 variant。`from.state` に配列を書くと state を限定できる。`requires[].same` に列挙した軸は goal と同じ target、それ以外は代表 target を使う。 |
| `matrix` | Member x Resource matrix に出す component と、goal state から期待値を決める `assertion`。 |
| `case_prerequisites` | 全シナリオ共通の前提条件。 |
| `required_placeholders` | 全シナリオが保持すべき placeholder。 |
| `closing_notes` | 全シナリオの後続確認に付ける注意。 |
| `case_list_rules` | ケース一覧の「枝刈り規則」表。 |

新しい API step を追加する場合は、`flow.manual.yaml`、`templates/steps/`、必要に応じて `steps/<group>/` を同時に更新する。`tests/tools/test_generate_e2e_specs.py` は API一覧のendpointがすべて `steps` に含まれることを検査する。

## 変更時の検証

```bash
uv run python -m tools.generate_e2e_case_list
uv run python -m tools.generate_e2e_scenarios
uv run python -m tools.check_e2e_specs
uv run pytest tests/tools/test_generate_e2e_specs.py
```

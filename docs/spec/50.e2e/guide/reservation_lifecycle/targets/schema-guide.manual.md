# targets YAML schema guide

## 対象ファイル

- `targets/members/<member>.target.manual.yaml`
- `targets/resources/<resource>.target.manual.yaml`

## 役割

E2E の対象軸に並ぶ論理対象を定義する。どの target を使うかは `flow.manual.yaml` の `target_dimensions[].targets` が正本で、そこに列挙した target の YAML がないと `check_e2e_specs` が失敗する。

## schema

```yaml
schema_version: 1

target:
  type: resource
  id: room_A
  title: Room A
  display_name: room_A
  description: E2Eで予約対象にするroom資源 Room A
  tags:
    - active_resource
    - room

md:
  target_section:
    resource_type: Resource
    usage: 予約対象資源
    show_variables:
      - resourceId

defaults:
  name: E2E 会議室A ${case.id}
  kind: room
```

`title` はケース一覧、matrix、シナリオの対象名に使う。`defaults` は `${resource.defaults.<key>}` / `${member.defaults.<key>}` で参照でき、値内の `${case.id}` も展開する。実在の利用者IDやtokenは書かず、`${actors.member_A}` や `${member_token}` のような placeholder にする。

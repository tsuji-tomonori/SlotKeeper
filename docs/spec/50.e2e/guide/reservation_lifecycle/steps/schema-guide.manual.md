# steps YAML schema guide

## 対象ファイル

- `steps/system_api/*.step.manual.yaml`
- `steps/resource_api/*.step.manual.yaml`
- `steps/reservation_api/*.step.manual.yaml`

## 役割

binding と evidence collector が参照する API 呼び出し step を定義する。シナリオの「操作」と「取得方法」は `step.title` と `step.endpoint` から生成する。

## schema

```yaml
schema_version: 1

step:
  id: reservation_create_reservation
  title: 予約作成APIを呼び出す
  phase: exercise
  operation_id: createReservation
  endpoint: POST /reservations

request:
  source: components/reservation_booking/data.manual.yaml#booking_default.request

expect:
  response:
    status: ${result.expected_status}

capture:
  reservationId[${member.id},${resource.id}]: $.reservationId
```

| フィールド | 内容 |
|---|---|
| `phase` | `setup`、`exercise`、`evidence`。 |
| `operation_id` | OpenAPI の operationId。 |
| `endpoint` | `METHOD path`。path parameter は `${name}`。 |
| `request.source` | data profile の request を参照する場合に書く。 |
| `capture` | 後続 step で使う値。target ごとに区別するため `[${member.id},${resource.id}]` を付ける。 |

binding または evidence collector から参照された step が存在しない場合、`check_e2e_specs` が失敗する。

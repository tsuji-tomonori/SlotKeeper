# templates YAML schema guide

## 対象ファイル

- `templates/steps/<template>.manual.yaml`

## 役割

`flow.manual.yaml` の `steps[].template` ごとに、HTTP 呼び出しの雛形を定義する。本文は実装の `samples.py` にある request sample を参照し、API 実装と E2E 仕様の入力形がずれないようにする。

## schema

```yaml
schema_version: 1
template:
  id: post_reservations
  operation_id: createReservation
  method: POST
  path: /reservations
request:
  headers:
    Authorization: Bearer ${tokens.member_token}
    Idempotency-Key: ${case.case_id}-reservation
  body:
    from_sample:
      module: app.apis.reservations.create_reservation.samples
      object: CREATE_RESERVATION_REQUEST_SAMPLE
captures:
  reservationId: $.reservationId
```

`check_e2e_specs` は、template の method/path/operation_id が `flow.manual.yaml` の step と一致すること、`from_sample` の module と object が import できることを検査する。

# reservations_create / Detail Design

## 1. 正常系入力

{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/BookingInput"
      }
    }
  },
  "required": true
}

## 2. 正常系前提

再送照合を新規時刻検証より先に行い、commit後だけ成功応答を返す。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| control | update | resources |
| create | insert | reservations |
| event | insert | reservation_events |
| expire | delete | idempotency_records |
| overlap | select | reservations |
| record | insert | idempotency_records |
| replay | select | idempotency_records |
| user | insert | users |

## 4. 正常系レスポンス

```json
{
  "201": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Reservation"
        }
      }
    },
    "description": "Successful Response"
  },
  "401": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Unauthorized"
  },
  "403": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Forbidden"
  },
  "404": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Not Found"
  },
  "409": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Conflict"
  },
  "422": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Unprocessable Entity"
  },
  "503": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ErrorBody"
        }
      }
    },
    "description": "Service Unavailable"
  }
}
```

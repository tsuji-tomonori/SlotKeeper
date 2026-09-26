# reservations_get / Detail Design

## 1. 正常系入力

[
  {
    "in": "path",
    "name": "reservation_id",
    "required": true,
    "schema": {
      "title": "Reservation Id",
      "type": "string"
    }
  }
]

## 2. 正常系前提

権限のある予約に限って操作履歴を含む詳細を返す。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| events | select | reservation_events |
| get | select | reservations |

## 4. 正常系レスポンス

```json
{
  "200": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Detail"
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

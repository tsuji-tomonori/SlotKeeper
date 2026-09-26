# reservations_cancel / Detail Design

## 1. 正常系入力

{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CancelInput"
      }
    }
  },
  "required": true
}

## 2. 正常系前提

所有者、公開版、状態と開始時刻を検査して取消と履歴を確定する。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| cancel | update | reservations |
| control | update | resources |
| event | insert | reservation_events |
| get | select | reservations |

## 4. 正常系レスポンス

```json
{
  "200": {
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

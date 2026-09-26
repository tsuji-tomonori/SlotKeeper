# schedule / Detail Design

## 1. 正常系入力

[
  {
    "in": "path",
    "name": "resource_id",
    "required": true,
    "schema": {
      "title": "Resource Id",
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "day",
    "required": true,
    "schema": {
      "format": "date",
      "title": "Day",
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 100,
      "maximum": 100,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    }
  },
  {
    "in": "query",
    "name": "offset",
    "required": false,
    "schema": {
      "default": 0,
      "minimum": 0,
      "title": "Offset",
      "type": "integer"
    }
  }
]

## 2. 正常系前提

一般利用者には他人の識別情報と目的を返さない。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| bookings | select | reservations |
| resource | select | resources |

## 4. 正常系レスポンス

```json
{
  "200": {
    "content": {
      "application/json": {
        "schema": {
          "items": {
            "$ref": "#/components/schemas/BusySlot"
          },
          "title": "Response Schedule",
          "type": "array"
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

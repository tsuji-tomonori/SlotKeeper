# resources_create / Detail Design

## 1. 正常系入力

{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ResourceInput"
      }
    }
  },
  "required": true
}

## 2. 正常系前提

管理者権限を確認して新しい資源を登録する。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| create | insert | resources |

## 4. 正常系レスポンス

```json
{
  "201": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Resource"
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

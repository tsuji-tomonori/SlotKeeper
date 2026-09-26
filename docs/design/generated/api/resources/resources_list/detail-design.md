# resources_list / Detail Design

## 1. 正常系入力

[
  {
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 50,
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

認証済み利用者へ固定順とページ単位で資源を返す。

## 3. 正常系リソース変更

| query | 操作 | 対象 |
| --- | --- | --- |
| select_page | select | resources |

## 4. 正常系レスポンス

```json
{
  "200": {
    "content": {
      "application/json": {
        "schema": {
          "items": {
            "$ref": "#/components/schemas/Resource"
          },
          "title": "Response Resources List",
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

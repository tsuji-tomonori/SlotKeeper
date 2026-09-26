# schedule / Interface

## Headers

```json
[]
```

## Path Parameters

```json
[
  {
    "in": "path",
    "name": "resource_id",
    "required": true,
    "schema": {
      "title": "Resource Id",
      "type": "string"
    }
  }
]
```

## Query Parameters

```json
[
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
```

## Data

```json
{}
```

## Responses

##### 200

```json
{
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
}
```

##### 401

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Unauthorized"
}
```

##### 403

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Forbidden"
}
```

##### 404

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Not Found"
}
```

##### 409

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Conflict"
}
```

##### 422

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Unprocessable Entity"
}
```

##### 503

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/ErrorBody"
      }
    }
  },
  "description": "Service Unavailable"
}
```

## Samples

### 公開契約

#### Request

`GET /resources/{resource_id}/schedule`。入力例と型はOpenAPIを参照。

#### Response

OpenAPIのresponse schemaに従う。実応答はテスト証跡に記録する。

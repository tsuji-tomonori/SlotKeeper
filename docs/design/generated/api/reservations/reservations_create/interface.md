# reservations_create / Interface

## Headers

```json
[
  {
    "in": "header",
    "name": "idempotency-key",
    "required": true,
    "schema": {
      "maxLength": 128,
      "minLength": 1,
      "pattern": "^[A-Za-z0-9_-]+$",
      "title": "Idempotency-Key",
      "type": "string"
    }
  }
]
```

## Path Parameters

```json
[]
```

## Query Parameters

```json
[]
```

## Data

```json
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
```

## Responses

##### 201

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/Reservation"
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

`POST /reservations`。入力例と型はOpenAPIを参照。

#### Response

OpenAPIのresponse schemaに従う。実応答はテスト証跡に記録する。

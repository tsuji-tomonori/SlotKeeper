# resources_create / Interface

## Headers

```json
[]
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
        "$ref": "#/components/schemas/ResourceInput"
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
        "$ref": "#/components/schemas/Resource"
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

`POST /resources`。入力例と型はOpenAPIを参照。

#### Response

OpenAPIのresponse schemaに従う。実応答はテスト証跡に記録する。

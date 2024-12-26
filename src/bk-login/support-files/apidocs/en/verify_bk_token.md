### Description

Verify bk_token

### Parameters

| Name     | Type   | Required | Description                                                       |
|----------|--------|----------|-------------------------------------------------------------------|
| bk_token | string | Yes      | User login state ticket, which needs to be retrieved from Cookies |

### Request Example

```json5
// URL Query Parameter
bk_token=bkcrypt%24gAAAAABnWEIbW4BC9VrczvN5pE-ga9fjq0JvT-ZbbjRRIYeVpGsRWWR3NASAzEDHGvPSjshkK-lqgUnqkDSNao58xTrbtCrDIQFrPlDmKXfXPvu2aLOVGz1mrzftygyAEHQ0G1HFXEexfn3CjkwedW5j2-Yu-GU5XA%3D%3D
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "bk_username": "nteuuhzxlh0jcanw",
    "tenant_id": "system"
  }
}

```

### Response Parameters Description

| Name        | Type   | Description                             |
|-------------|--------|-----------------------------------------|
| bk_username | string | User unique identifier, globally unique |
| tenant_id   | string | User's tenant ID                        |

### Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Login session has expired"
  }
}
```

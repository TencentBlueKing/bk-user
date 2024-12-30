### Description

Query user's detailed information

### Parameters

| Name        | Type   | Required | Description                |
|-------------|--------|----------|----------------------------|
| bk_username | string | Yes      | Blueking unique identifier |

### Request Example

```
// URL Path Parameter
/api/open/v3/tenant/users/{bk_username}/
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "tenant_id": "default",
    "bk_username": "7idwx3b7nzk6xigs",
    "display_name": "张三",
    "time_zone": "Asia/Shanghai",
    "language": "zh-cn",
  }
}
```

### Response Parameters Description

| Name         | Type   | Description                |
|--------------|--------|----------------------------|
| tenant_id    | string | Tenant ID                  |
| bk_username  | string | Blueking unique identifier |
| display_name | string | User's display_name        |
| time_zone    | string | Time Zone                  |
| language     | string | Language                   |

# Response Example for Non-200 Status Code

```json5
// status_code = 404
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Object not found"
  }
}
```

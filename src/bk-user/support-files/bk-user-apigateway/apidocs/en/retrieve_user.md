### Description

Query user's information

### Parameters

| Name        | Type   | Required | Description                       |
|-------------|--------|----------|-----------------------------------|
| bk_username | string | Yes      | Blueking user's unique identifier |

### Request Example

```
// URL Path Parameter
/api/open/v3/tenant/users/7idwx3b7nzk6xigs/
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "tenant_id": "default",
        "bk_username": "7idwx3b7nzk6xigs",
        "login_name": "zhangsan",
        "display_name": "zhangsan(张三)",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
        "status": "enabled"
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                                                                |
|--------------|--------|----------------------------------------------------------------------------|
| tenant_id    | string | Tenant ID                                                                  |
| bk_username  | string | Blueking user's unique identifier                                          |
| login_name   | string | Unique ID of the user within the enterprise                                |
| display_name | string | User's display_name                                                        |
| time_zone    | string | Time Zone                                                                  |
| language     | string | Language                                                                   |
| status       | string | User's status, including the states of 'enabled', 'disabled' and 'expired' |

### Description

Query user's display information

### Parameters

| Name        | Type   | Required | Description                       |
|-------------|--------|----------|-----------------------------------|
| bk_username | string | Yes      | Blueking user's unique identifier |

### Request Example

```
// URL Path Parameters
/api/v3/open-web/tenant/users/7idwx3b7nzk6xigs/display_info/
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "login_name": "zhangsan",
        "full_name": "张三",
        "display_name": "zhangsan(张三)"
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| login_name   | string | Unique ID of the user within the enterprise |
| full_name    | string | User's name                                 |
| display_name | string | User's display_name                         |

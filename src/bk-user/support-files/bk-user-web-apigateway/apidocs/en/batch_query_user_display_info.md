### Description

Batch query user's display information

### Parameters

| Name         | Type   | Required | Description                                                                                           |
|--------------|--------|----------|-------------------------------------------------------------------------------------------------------|
| bk_usernames | string | Yes      | Blueking user's unique identifier, multiple identifiers are separated by commas, and the limit is 100 |

### Request Example

```
// URL Query Parameters
bk_usernames=7idwx3b7nzk6xigs,0wngfim3uzhadh1w
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
            "full_name": "李四",
            "display_name": "lisi(李四)"
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| bk_username  | string | Blueking user's unique identifier           |
| login_name   | string | Unique ID of the user within the enterprise |
| full_name    | string | User's name                                 |
| display_name | string | User's display_name                         |

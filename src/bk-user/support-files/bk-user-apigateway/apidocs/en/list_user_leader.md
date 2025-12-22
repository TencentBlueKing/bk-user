### Description

Query user's list of leaders

### Parameters

| Name           | Type    | Required | Description                                    |
|----------------|---------|----------|------------------------------------------------|
| bk_username    | string  | Yes      | Blueking user's unique identifier              |

### Request Example

```
// URL Path Parameter
/api/v3/open/tenant/users/mzmwjffhhbjg4fxz/leaders/
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "q9k6bhqks0ckl5ew",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)"
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "login_name": "zhangsan",
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
| display_name | string | User's display name                         |

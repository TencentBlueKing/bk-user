### Description

(Pagination) Query user's list

### Parameters

| Name      | Type | Required | Description                                                  |
|-----------|------|----------|--------------------------------------------------------------|
| page      | int  | No       | Page number, default is 1                                    |
| page_size | int  | No       | The number of pages per page, default is 10, maximum is 1000 |

### Request Example

```
// URL Query Parameters
page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "count": 2,
        "results": [
            {
                "bk_username": "q9k6bhqks0ckl5ew",
                "full_name": "张三",
                "display_name": "zhangsan(张三)",
                "status": "enabled"
            },
            {
                "bk_username": "er0ugcammqwf1q5w",
                "full_name": "李四",
                "display_name": "lisi(李四)",
                "status": "disabled"
            }
        ]
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                                                                |
|--------------|--------|----------------------------------------------------------------------------|
| bk_username  | string | Blueking user's unique identifier                                          |
| full_name    | string | User's name                                                                |
| display_name | string | User's display name                                                        |
| status       | string | User's status, including the states of 'enabled', 'disabled' and 'expired' |

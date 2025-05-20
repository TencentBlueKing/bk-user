### Description

(Pagination) Query user's list

### Parameters

| Name      | Type | Required | Description                                                 |
|-----------|------|----------|-------------------------------------------------------------|
| page      | int  | No       | Page number, default is 1                                   |
| page_size | int  | No       | The number of pages per page, default is 10, maximum is 500 |

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
                "bk_username": "klzwge6k69ly0rjt",
                "login_name": "virtual_user_1",
                "full_name": "虚拟用户1",
                "display_name": "virtual_user_1(虚拟用户1)"
             },
             {
                "bk_username": "soxteugr5ymfi3w1",
                "login_name": "virtual_user_2",
                "full_name": "虚拟用户2",
                "display_name": "virtual_user_2(虚拟用户2)"
            }
        ]
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                                                                |
|--------------|--------|----------------------------------------------------------------------------|
| bk_username  | string | Blueking user's unique identifier                                          |
| login_name   | string | Unique ID of the user within the enterprise                                |
| full_name    | string | User's name                                                                |
| display_name | string | User's display name                                                        |
| status       | string | User's status, including the states of 'enabled', 'disabled' and 'expired' |

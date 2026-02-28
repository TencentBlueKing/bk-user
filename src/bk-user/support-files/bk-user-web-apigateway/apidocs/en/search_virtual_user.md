### Description

Search virtual users. The search results return the first 100 data by default (If you need more search results, you need to refine the search conditions)

### Parameters

| Name    | Type   | Required | Description                                                                                                                        |
|---------|--------|----------|------------------------------------------------------------------------------------------------------------------------------------|
| keyword | string | Yes      | Search keywords (you can enter the values of login_name or full_name). The minimum input length is 1 and the maximum input length is 64 |

### Request Example

```
// URL Query Parameters
keyword=zhang
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "klzwge6k69ly0rjt",
            "login_name": "virtual_user_1",
            "full_name": "虚拟用户1",
            "display_name": "virtual_user_1(虚拟用户1)",
            "status": "enabled"
        },
        {
            "bk_username": "soxteugr5ymfi3w1",
            "login_name": "virtual_user_2",
            "full_name": "虚拟用户2",
            "display_name": "virtual_user_2(虚拟用户2)",
            "status": "enabled"
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                                                                     |
|--------------|--------|---------------------------------------------------------------------------------|
| bk_username  | string | Blueking user's unique identifier                                               |
| login_name   | string | Unique ID of the user within the enterprise                                     |
| full_name    | string | User's name                                                                     |
| display_name | string | User's display name                                                             |
| status       | string | User's status, including the states of 'enabled', 'disabled' and 'expired'      |

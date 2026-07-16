### Description

Batch query the information of users

### Parameters

| Name         | Type   | Required | Description                                                                                                                                     |
|--------------|--------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| lookups      | string | Yes      | Exact lookup values (can be bk_username、login_name), multiple separated by separator, limit number is 100, maximum input length per value is 64 |
| lookup_field | string | Yes      | Lookup field, can be selected from the value of `bk_username`, `login_name`                                                                     |

### Request Example

```
// URL Query Parameter
lookups=zhangsan,lisi&lookup_field=login_name
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "status": "enabled",
            "language": "zh-cn",
            "time_zone": "Asia/Shanghai"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
            "full_name": "李四",
            "display_name": "lisi(李四)",
            "status": "enabled",
            "language": "en",
            "time_zone": "Asia/Shanghai"
        }
    ]
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
| language     | string | User's language preference                                                 |
| time_zone    | string | User's time zone                                                           |

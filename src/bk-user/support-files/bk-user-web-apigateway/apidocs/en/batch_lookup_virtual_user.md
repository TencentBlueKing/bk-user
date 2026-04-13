### Description

Batch query virtual users

### Parameters

| Name          | Type   | Required | Description                                                                                                                                                  |
|---------------|--------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| lookups       | string | Yes      | Exact matching values (can be bk_username, login_name or full_name), multiple separated by commas, limit number is 100, maximum input length per value is 64 |
| lookup_fields | string | Yes      | Matching fields, multiple separated by commas, the optional values of each element are `bk_username`, `login_name`, `full_name`                              |

### Request Example

```
// URL Query Parameters
lookups=zhangsan,lisi&lookup_fields=login_name,bk_username
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
| display_name | string | User's display name                         |

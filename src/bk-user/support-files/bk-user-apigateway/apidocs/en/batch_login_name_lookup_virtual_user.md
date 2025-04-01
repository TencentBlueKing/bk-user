### Description

Batch query virtual user's information by login_names

### Parameters

| Name        | Type   | Required | Description                                                                                                     |
|-------------|--------|----------|-----------------------------------------------------------------------------------------------------------------|
| login_names | string | Yes      | Unique ID of the user within the enterprise, multiple identifiers are separated by commas, and the limit is 100 |

### Request Example

```
// URL Query Parameter
login_names=zhangsan,lisi
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "display_name": "zhangsan(张三)"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
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
| display_name | string | User's display_name                         |

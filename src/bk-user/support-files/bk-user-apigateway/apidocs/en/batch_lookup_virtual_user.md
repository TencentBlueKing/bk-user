### Description

Batch query virtual user's information

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

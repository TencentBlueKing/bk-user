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
lookups=virtual_user_1,virtual_user_2&lookup_field=login_name
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "virtual_user_1",
            "full_name": "虚拟用户1",
            "display_name": "virtual_user_1(虚拟用户1)"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "virtual_user_2",
            "full_name": "虚拟用户2",
            "display_name": "virtual_user_2(虚拟用户2)"
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

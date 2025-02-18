### Description

Batch query user's display_info

### Parameters

| Name         | Type   | Required | Description                                                                                           |
| ------------ | ------ | -------- | ----------------------------------------------------------------------------------------------------- |
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
            "display_name": "张三"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "display_name": "李四"
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                       |
| ------------ | ------ | --------------------------------- |
| bk_username  | string | Blueking user's unique identifier |
| display_name | string | User's display_name               |

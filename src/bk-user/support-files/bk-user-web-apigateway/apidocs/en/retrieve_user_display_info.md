### Description

Query user's display information

### Parameters

| Name        | Type   | Required | Description                       |
| ----------- | ------ | -------- | --------------------------------- |
| bk_username | string | Yes      | Blueking user's unique identifier |

### Request Example

```
// URL Path Parameters
/api/v3/open/frontend/tenant/users/7idwx3b7nzk6xigs/display_info/
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "display_name": "张三"
    }
}
```

### Response Parameters Description

| Name         | Type   | Description         |
| ------------ | ------ | ------------------- |
| display_name | string | User's display_name |

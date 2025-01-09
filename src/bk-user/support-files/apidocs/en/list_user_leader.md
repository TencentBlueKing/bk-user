### Description

Query user's list of leaders

### Parameters

| Name           | Type    | Required | Description                                    |
|----------------|---------|----------|------------------------------------------------|
| bk_username    | string  | Yes      | Blueking user's unique identifier              |

### Request Example

```
// URL Path Parameter
/api/v3/open/tenant/users/mzmwjffhhbjg4fxz/leaders/
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "q9k6bhqks0ckl5ew",
            "display_name": "张三"
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "display_name": "李四"
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                       |
|--------------|--------|-----------------------------------|
| bk_username  | string | Blueking user's unique identifier |
| display_name | string | User's display_name               |


# Response Example for Non-200 Status Code

```json5
// status_code = 404
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Object not found"
  }
}
```

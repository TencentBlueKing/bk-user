### Description

(Pagination) Query the list of virtual user's information

### Parameters

| Name       | Type   | Required | Description                                                 |
|------------|--------|----------|-------------------------------------------------------------|
| login_name | string | No       | Unique ID of the user within the enterprise                 |
| page       | int    | No       | Page number, default is 1                                   |
| page_size  | int    | No       | The number of pages per page, default is 10, maximum is 500 |

### Request Example

```
// URL Query Parameter
login_name=bk_admin&page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "count": 1,
        "results": [
            {
                "bk_username": "q9k6bhqks0ckl5ew",
                "login_name": "bk_admin",
                "display_name": "bk_admin"
            }
        ]
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| bk_username  | string | Blueking user's unique identifier           |
| login_name   | string | Unique ID of the user within the enterprise |
| display_name | string | User's display_name                         |

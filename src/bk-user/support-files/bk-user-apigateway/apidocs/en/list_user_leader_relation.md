### Description

(Pagination) Query list of relations between users and leaders

### Parameters

| Name      | Type | Required | Description                                                 |
|-----------|------|----------|-------------------------------------------------------------|
| page      | int  | No       | Page number, default is 1                                   |
| page_size | int  | No       | The number of pages per page, default is 10, maximum is 500 |

### Request Example

```
// URL Query Parameters
page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "count": 2,
        "results": [
            {
                "bk_username": "q9k6bhqks0ckl5ew",
                "leader_bk_username": "mzkampfs7tf57rpg",
            },
            {
                "bk_username": "er0ugcammqwf1q5w",
                "leader_bk_username": "zxp8d1467qmu4ipb",
            }
        ]
    }
}
```

### Response Parameters Description

| Name               | Type   | Description                       |
|--------------------|--------|-----------------------------------|
| bk_username        | string | Blueking user's unique identifier |
| leader_bk_username | string | User leaders' unique identifier   |

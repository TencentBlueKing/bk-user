### Description

(Pagination) Query list of relations between users and departments

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
                "department_id": "1",
            },
            {
                "bk_username": "er0ugcammqwf1q5w",
                "department_id": "2",
            }
        ]
    }
}
```

### Response Parameters Description

| Name          | Type   | Description                         |
|---------------|--------|-------------------------------------|
| bk_username   | string | Blueking user's unique identifier   |
| department_id | string | Unique identifier of the department |

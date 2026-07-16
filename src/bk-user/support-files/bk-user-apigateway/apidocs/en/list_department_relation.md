### Description

(Pagination) Query list of relations between departments

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
                "id": 1,
                "parent_id": null,
            },
            {
                "id": 2,
                "parent_id": 1,
            }
        ]
    }
}
```

### Response Parameters Description

| Name          | Type | Description                                                                |
|---------------|------|----------------------------------------------------------------------------|
| department_id | int  | Unique identifier of the department                                        |
| parent_id     | int  | The parent department ID (If it is null, it indicates the root department) |

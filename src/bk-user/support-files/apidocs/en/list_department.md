### Description

(Pagination) Query list of departments

### Parameters

| Name      | Type | Required | Description                                 |
|-----------|------|----------|---------------------------------------------|
| page      | int  | No       | Page number, default is 1                   |
| page_size | int  | No       | The number of pages per page, default is 10 |

### Request Example

```
// URL Query Parameters
page=2&page_size=2
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": 3,
        "name": "部门B",
        "parent_id": 1,
      },
      {
        "id": 4,
        "name": "中心AA",
        "parent_id": 2,
      }
    ],
  }
}
```

### Response Parameters Description

| Name      | Type   | Description                         |
|-----------|--------|-------------------------------------|
| id        | int    | Unique identifier of the department |
| name      | string | The name of the department          |
| parent_id | int    | The parent department ID            |

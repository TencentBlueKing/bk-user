### Description

(Pagination) Query list of departments

### Parameters

| Name      | Type | Required | Description                                                                                     |
|-----------|------|----------|-------------------------------------------------------------------------------------------------|
| page      | int  | No       | Page number, default is 1                                                                       |
| page_size | int  | No       | The number of pages per page, default is 10                                                     |
| parent_id | int  | No       | Parent department ID, precise query parameter, if not provided, all departments will be queried |

### Request Example

```
// URL Query Parameters
page=1&page_size=5&parent_id=1
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": 2,
        "name": "部门A",
        "parent_id": 1,
      },
      {
        "id": 3,
        "name": "部门B",
        "parent_id": 1,
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


# Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Parameter validation failed: parent_id: The specified parent department does not exist in the current tenant"
  }
}
```

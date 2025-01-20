### Description

(Pagination) Query the sub-department list based on the department ID, support recursive query by level

### Parameters

| Name          | Type | Required | Location    | Description                                                                                                 |
|---------------|------|----------|-------------|-------------------------------------------------------------------------------------------------------------|
| page          | int  | No       | query param | Page number, default is 1                                                                                   |
| page_size     | int  | No       | query param | The number of pages per page, default is 10                                                                 |
| department_id | int  | Yes      | path        | Unique identifier of the department                                                                         |
| level         | int  | No       | query param | The relative level of the recursive sub-department. The default is 1, which means the direct sub-department |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/departments/2/childrens/?level=2&page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": 6,
        "name": "小组AAA",
      },
      {
        "id": 7,
        "name": "小组ABA",
      }
    ],
  }
}
```

### Response Parameters Description

| Name | Type   | Description                         |
|------|--------|-------------------------------------|
| id   | int    | Unique identifier of the department |
| name | string | The name of the department          |

For example, if the sub-departments of Department A are Center AA and Center AB, the sub-department of Center AA is
Group AAA, and the sub-department of Center AB is Group ABA, then the sub-department of Department A with a relative
level of level 2 is: Group AAA -> Group ABA

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

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Parameter validation failed: level: level must be greater than or equal to 1"
  }
}
```

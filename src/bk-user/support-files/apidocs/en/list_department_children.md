### Description

(Pagination) Query the sub-department list based on the department ID

### Parameters

| Name          | Type | Required | Location    | Description                                                    |
|---------------|------|----------|-------------|----------------------------------------------------------------|
| page          | int  | No       | query param | Page number, default is 1                                      |
| page_size     | int  | No       | query param | The number of pages per page, default is 10                    |
| department_id | int  | Yes      | path        | Unique identifier of the department                            |
| is_recursive  | bool | No       | query param | Whether to recursively query sub-departments, default is false |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/departments/2/childrens/?is_recursive=true&page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 4,
    "results": [
      {
        "id": 4,
        "name": "中心AA",
      },
      {
        "id": 6,
        "name": "小组AAA",
      },
      {
        "id": 5,
        "name": "中心AB",
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

If ***is_recursive*** is true, all sub-departments are returned recursively by level. For example, the sub-departments
of department A are center AA and center AB, the sub-department of center AA is group AAA, and the sub-department of
center AB is group ABA. Then the sub-department list of department A is returned in the following order: center AA ->
group AAA -> center AB -> group ABA.

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

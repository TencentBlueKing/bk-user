### Description

(Pagination) Query the user list under the department according to the department ID

### Parameters

| Name          | Type | Required | Location    | Description                                                                                                         |
|---------------|------|----------|-------------|---------------------------------------------------------------------------------------------------------------------|
| page          | int  | No       | query param | Page number, default is 1                                                                                           |
| page_size     | int  | No       | query param | The number of pages per page, default is 10                                                                         |
| department_id | int  | Yes      | path        | Unique identifier of the department                                                                                 |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/departments/2/users/?page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "bk_username": "q9k6bhqks0ckl5ew",
        "full_name": "张三",
        "display_name": "张三",
      },
      {
        "bk_username": "er0ugcammqwf1q5w",
        "full_name": "李四",
        "display_name": "李四",
      }
    ],
  }
}
```

### Response Parameters Description

| Name         | Type   | Description                       |
|--------------|--------|-----------------------------------|
| bk_username  | string | Blueking user's unique identifier |
| full_name    | string | User's name                       |
| display_name | string | User's display name               |


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

### Description

Query information of the department(supports whether to include ancestor departments)

### Parameters

| Name           | Type    | Required | Location    | Description                                    |
|----------------|---------|----------|-------------|------------------------------------------------|
| department_id  | int     | Yes      | path        | Unique identifier of the department            |
| with_ancestors | boolean | No       | query param | Whether to include ancestors, default is false |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/departments/3/?with_ancestors=true
```

### Response Example for Status Code 200

```json5
{
  "id": 3,
  "name": "部门C",
  "ancestors": [
    {
      "id": 1,
      "name": "部门A"
    },
    {
      "id": 2,
      "name": "部门B"
    }
  ]
}
```

### Response Parameters Description

| Name      | Type   | Description                                                                                                                                                                 |
|-----------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id        | int    | Unique identifier of the department                                                                                                                                         |
| name      | string | The name of the department                                                                                                                                                  |
| ancestors | array  | List of ancestor departments, the order is from the root department to the immediate parent department, for example: "company" -> "department A" -> "center B" -> "group C" |

**Ancestors** is a list of ancestor departments. Each element in the list is the ancestor department information of the
user's department, arranged in descending order (from root department -> immediate parent department), for
example: If the user department is **team AAA** and the parent department is **center AA**, then the order in the
ancestor department list could be `company -> department A -> center AA`. Each ancestor department contains the
following parameters:

| Name | Type   | Description                         |
|------|--------|-------------------------------------|
| id   | int    | Unique identifier of the department |
| name | string | The name of the department          |

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

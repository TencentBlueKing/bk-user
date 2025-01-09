### Description

Query information of the department(supports whether to include ancestor departments)

### Parameters

| Name           | Type    | Required | Description                                    |
|----------------|---------|----------|------------------------------------------------|
| department_id  | int     | Yes      | Tenant department ID                           |
| with_ancestors | boolean | No       | Whether to include ancestors, default is false |

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

| Name      | Type   | Description                  |
|-----------|--------|------------------------------|
| id        | int    | Tenant department ID         |
| name      | string | Tenant department name       |
| ancestors | list   | List of ancestor departments |

#### Ancestors Parameters Description

**Ancestors** is a list of ancestor departments. Each element in the list is the ancestor department information of the
user's department, arranged in descending order (from root ancestor department -> parent department), for
example: If the user department is **team AAA** and the parent department is **center AA**, then the order in the
ancestor department list could be `company -> department A -> center AA`. Each ancestor department contains the
following parameters:

| Name | Type   | Description              |
|------|--------|--------------------------|
| id   | int    | Ancestor department ID   |
| name | string | Ancestor department name |

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

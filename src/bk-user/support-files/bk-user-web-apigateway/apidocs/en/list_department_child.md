### Description

Get a list of sub-departments (including collaborations) of a department

### Parameters

| Name                 | Type   | Required | Location    | Description                                                                                          |
|----------------------|--------|----------|-------------|------------------------------------------------------------------------------------------------------|
| parent_department_id | int    | Yes      | path        | Unique ID of the department (0 or no entry means the root department is obtained by default)         |
| owner_tenant_id      | string | No       | query_param | The tenant ID to which the data source belongs, if department_id is 0, you must input this parameter |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open-web/tenant/departments/1/children/
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "has_child": true,
            "has_user": true,
            "ancestors": [{"id": 1, "name": "公司"}, {"id": 2, "name": "部门A"}]
        },
        {
            "id": 5,
            "name": "中心AB",
            "has_child": false,
            "has_user": true,
            "ancestors": [{"id": 1, "name": "公司"}, {"id": 2, "name": "部门A"}]
        }
    ]
}
```

### Response Parameters Description

| Name      | Type   | Description                         |
|-----------|--------|-------------------------------------|
| id        | int    | Unique identifier of the department |
| name      | string | The name of the department          |
| has_child | bool   | Whether the department has children |
| has_user  | bool   | Whether the department has users    |
| ancestors | array  | Ancestor departments (from the root department to the parent department, excluding itself) |
| ancestors[].id   | int    | Unique identifier of the ancestor department, `null` if the department has not been synchronized to the current tenant |
| ancestors[].name | string | Ancestor department name |

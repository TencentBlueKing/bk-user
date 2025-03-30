### Description

Batch query the departments (including collaborative departments)

### Parameters

| Name            | Type   | Required | Description                                                                                                                                                                                                                                       |
|-----------------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| department_ids  | string | Yes      | Unique ID of the department, multiple separated by separator, limit number is 100                                                                                                                                                                 |

### Request Example

```
// URL Query Parameters
department_ids=4,5
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "owner_tenant_id": "default",
            "organization_path": "公司/部门A",
        },
        {
            "id": 5,
            "name": "中心AB",
            "owner_tenant_id": "collaborative_tenant",
            "organization_path": "公司/部门A",
        }
    ]
}
```

### Response Parameters Description

| Name              | Type   | Description                                                                                                                                                    |
|-------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                | int    | Unique identifier of the department                                                                                                                            |
| name              | string | Department name                                                                                                                                                |
| owner_tenant_id   | string | The tenant ID to which the data source belongs. The tenant user is returned as the tenant ID, and the collaborative user is returned as the original tenant ID |
| organization_path | string | Department organizational path, format: `Department 1/Department 2/.../Department n`                                                                           |

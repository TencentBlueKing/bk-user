### Description

Batch query the departments (including collaborative departments)

### Parameters

| Name            | Type   | Required | Description                                                                                                                                                                                                                                       |
|-----------------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| department_ids  | string | Yes      | Unique ID of the department, multiple separated by separator, limit number is 100                                                                                                                                                                 |
| owner_tenant_id | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to search the corresponding tenant departments. The default value is empty (search the departments of this tenant and the departments of the collaborative tenants) |

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

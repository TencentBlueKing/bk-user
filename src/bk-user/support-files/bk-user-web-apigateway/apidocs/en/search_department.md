### Description

Search departments (including collaborative departments). The search results will return the first 100 data by default (if you need more search results, you need to refine the search conditions)

### Parameters

| Name            | Type   | Required | Description                                                                                                                                                                                                                                       |
|-----------------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| keyword         | string | Yes      | Search keywords (you can enter the name of department). The minimum input length is 1 and the maximum input length is 64                                                                                                                          |
| owner_tenant_id | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to search the corresponding tenant departments. The default value is empty (search the departments of this tenant and the departments of the collaborative tenants) |

### Request Example

```
// URL Query Parameters
keyword=中心A
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
            "has_child": false,
            "has_user": true
        },
        {
            "id": 5,
            "name": "中心AB",
            "owner_tenant_id": "collaborative_tenant",
            "organization_path": "公司/部门A",
            "has_child": false,
            "has_user": false
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
| has_child         | bool   | Whether the department has sub-departments                                                                                                                     |
| has_user          | bool   | Whether the department has users                                                                                                                               |

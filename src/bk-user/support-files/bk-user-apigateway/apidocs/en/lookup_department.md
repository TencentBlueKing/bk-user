### Description

Batch query the information of the departments

### Parameters

| Name           | Type   | Required | Description                                                                      |
|----------------|--------|----------|----------------------------------------------------------------------------------|
| department_ids | string | Yes      | Unique ID of the department, multiple separated by separator, limit number is 50 |
| with_org_path  | bool   | No       | Whether to return the organizational path of the department, default is `false`  |

### Request Example

```
// URL Query Parameters
department_ids=4,5&with_org_path=true
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "organization_path": "公司/部门A",
        },
        {
            "id": 5,
            "name": "中心AB",
            "organization_path": "公司/部门A",
        }
    ]
}
```

### Response Parameters Description

| Name              | Type   | Description                                                                          |
|-------------------|--------|--------------------------------------------------------------------------------------|
| id                | int    | Unique identifier of the department                                                  |
| name              | string | Department name                                                                      |
| organization_path | string | Department organizational path, format: `Department 1/Department 2/.../Department n` |

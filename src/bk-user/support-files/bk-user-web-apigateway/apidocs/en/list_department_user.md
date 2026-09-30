### Description

Query the user list under the department according to the department ID

### Parameters

| Name            | Type   | Required | Location    | Description                                                                                                                                 |
|-----------------|--------|----------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| department_id   | int    | Yes      | path        | Unique ID of the department (if it is 0 or not filled in, no department is specified, and users without department are returned by default) |
| owner_tenant_id | string | No       | query param | The tenant ID to which the data source belongs, if department_id is 0, you must input this parameter                                        |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open-web/tenant/departments/1/users/
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "q9k6bhqks0ckl5ew",
            "login_name": "zhangsan",
            "display_name": "zhangsan(张三)",
            "organizations": [
                [{"id": 1, "name": "公司"}]
            ]
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "login_name": "lisi",
            "display_name": "lisi(李四)",
            "organizations": [
                [{"id": 1, "name": "公司"}],
                [{"id": 1, "name": "公司"}, {"id": 2, "name": "部门A"}]
            ]
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| bk_username  | string | Blueking user's unique identifier           |
| login_name   | string | Unique ID of the user within the enterprise |
| display_name | string | User's display name                         |
| organizations | array | The organization chains to which the user belongs, one chain per direct department (from the root department to the direct department, inclusive) |
| organizations[][].id   | int    | Unique identifier of the department, `null` if the department has not been synchronized to the current tenant |
| organizations[][].name | string | Department name |

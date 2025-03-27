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
            "display_name": "张三"
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "login_name": "lisi",
            "display_name": "李四"
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

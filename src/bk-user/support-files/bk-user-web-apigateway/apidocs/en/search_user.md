### Description

Search user (including collaborative users). The search results return the first 100 data by default (If you need more search results, you need to refine the search conditions)

### Parameters

| Name                    | Type   | Required | Description                                                                                                                                                                                                                   |
|-------------------------|--------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| keyword                 | string | Yes      | Search keywords (you can enter the values of login_name (unique ID of user in the enterprise) or full_name (name)). The minimum input length is 1 and the maximum input length is 64                                          |
| owner_tenant_id         | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to search the corresponding tenant users. The default value is empty (search the users of this tenant and the users of the cooperating tenants) |
| with_organization_paths | bool   | No       | Whether to return the organization paths of the user. The default value is `false`                                                                                                                                            |

### Request Example

```
// URL Query Parameters
keyword=zhang&with_organization_paths=true
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "hc6n2ydjxtxef4cw",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "owner_tenant_id": "default",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AA"],
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "full_name": "张四",
            "display_name": "zhangsi(张四)",
            "owner_tenant_id": "collaborative_tenant",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AB", "公司/部门B/中心BA"],
        },
    ]
}
```

### Response Parameters Description

| Name               | Type   | Description                                                                                                                                  |
|--------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------|
| bk_username        | string | Blueking user's unique identifier                                                                                                            |
| login_name         | string | Unique ID of the user within the enterprise                                                                                                  |
| full_name          | string | User's name                                                                                                                                  |
| display_name       | string | User's display name                                                                                                                          |
| owner_tenant_id    | string | The tenant ID to which the data source belongs. The tenant user is returned as the tenant ID, and the collaborative user is returned as the original tenant ID |
| status             | string | User's status, including the states of 'enabled', 'disabled' and 'expired'                                                                   |
| organization_paths | array  | The organization paths to which the user belongs, separated by commas, with the format of `Department 1/Department 2/.../Department n`       |

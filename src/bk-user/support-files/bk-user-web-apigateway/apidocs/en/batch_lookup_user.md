### Description

Batch query the users (including collaborative users and virtual users)

### Parameters

| Name                    | Type   | Required | Description                                                                                                                                                                                                                 |
|-------------------------|--------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| lookups                 | string | Yes      | Exact matching value (can be bk_username、login_name or full_name), multiple separated by separator, limit number is 100, maximum input length per value is 64                                                               |
| lookup_fields           | string | Yes      | Matching fields, multiple separated by commas, the optional values of each element are `bk_username`, `login_name`, `full_name`                                                                                             |
| data_source_type        | string | No       | Data source type, optional values are `real` (corresponding to real users) and `virtual` (corresponding to virtual users). The default value is empty (query real & virtual users)                                          |
| owner_tenant_id         | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to query the corresponding tenant users. The default value is empty (query the users of this tenant and the users of the cooperating tenants) |
| with_organization_paths | bool   | No       | Whether to return the organization paths of the user. The default value is `false`                                                                                                                                          |

### Request Example

```
// URL Query Parameters
lookups=zhangsan,lisi&lookup_fields=login_name,bk_username&with_organization_paths=true
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
            "data_source_type": "real",
            "owner_tenant_id": "default",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AA"],
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "lisi",
            "full_name": "李四",
            "display_name": "lisi(李四)",
            "data_source_type": "real",
            "owner_tenant_id": "collaborative_tenant",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AB", "公司/部门B/中心BA"],
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "data_source_type": "virtual",
            "owner_tenant_id": "default",
            "status": "disabled",
            "organization_paths": [],
        },
    ]
}
```

### Response Parameters Description

| Name               | Type   | Description                                                                                                                                                                              |
|--------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bk_username        | string | Blueking user's unique identifier                                                                                                                                                        |
| login_name         | string | Unique ID of the user within the enterprise                                                                                                                                              |
| full_name          | string | User's name                                                                                                                                                                              |
| display_name       | string | User's display_name                                                                                                                                                                      |
| data_source_type   | string | Data source type, where `real` corresponds to real-name data source (user), and `virtual` corresponds to virtual data source (user)                                                      |
| owner_tenant_id    | string | The tenant ID to which the data source belongs. The tenant user (including virtual users) is returned as the tenant ID, and the collaborative user is returned as the original tenant ID |
| status             | string | User's status, including the states of 'enabled', 'disabled' and 'expired'                                                                                                               |
| organization_paths | array  | The organization paths to which the user belongs, separated by commas, with the format of `Department 1/Department 2/.../Department n`; virtual users have no organization path          |

### Description

Batch query the users (including collaborative users and virtual users)

### Parameters

| Name             | Type   | Required | Description                                                                                                                                                                                                                 |
|------------------|--------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| lookups          | string | Yes      | Exact matching value (can be bk_username、login_name or full_name), multiple separated by separator, limit number is 100, maximum input length per value is 64                                                               |
| lookup_fields    | string | Yes      | Matching fields, multiple separated by commas, the optional values of each element are `bk_username`, `login_name`, `full_name`                                                                                             |
| data_source_type | string | No       | Data source type, optional values are `real` (corresponding to real users) and `virtual` (corresponding to virtual users). The default value is empty (query real & virtual users)                                          |
| owner_tenant_id  | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to query the corresponding tenant users. The default value is empty (query the users of this tenant and the users of the cooperating tenants) |

### Request Example

```
// URL Query Parameters
lookups=zhangsan,lisi&lookup_fields="login_name,bk_username"
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "hc6n2ydjxtxef4cw",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "张三",
            "data_source_type": "real",
            "owner_tenant_id": "default",
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "full_name": "张四",
            "display_name": "张四",
            "data_source_type": "real",
            "owner_tenant_id": "collaborative_tenant",
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangwu",
            "full_name": "张五",
            "display_name": "张五",
            "data_source_type": "virtual",
            "owner_tenant_id": "default",
        },
    ]
}
```

### Response Parameters Description

| Name             | Type   | Description                                                                                                                                                                              |
|------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bk_username      | string | Blueking user's unique identifier                                                                                                                                                        |
| login_name       | string | Unique ID of the user within the enterprise                                                                                                                                              |
| full_name        | string | User's name                                                                                                                                                                              |
| display_name     | string | User's display_name                                                                                                                                                                      |
| data_source_type | string | Data source type, where `real` corresponds to real-name data source (user), and `virtual` corresponds to virtual data source (user)                                                      |
| owner_tenant_id  | string | The tenant ID to which the data source belongs. The tenant user (including virtual users) is returned as the tenant ID, and the collaborative user is returned as the original tenant ID |

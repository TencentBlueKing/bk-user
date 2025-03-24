### Description

Search user (including collaborative users and virtual users). The search results return the first 100 data by default (If you need more search results, you need to refine the search conditions)

### Parameters

| Name             | Type   | Required | Description                                                                                                                                                                                                                   |
|------------------|--------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| keyword          | string | Yes      | Search keywords (you can enter the values of login_name (unique ID of user in the enterprise) or full_name (name)). The minimum input length is 2 and the maximum input length is 64                                          |
| data_source_type | string | No       | Data source type, optional values are `real` (corresponding to real users) and `virtual` (corresponding to virtual users). The default value is empty (search real & virtual users)                                           |
| owner_tenant_id  | string | No       | The tenant ID to which the data source belongs. You can specify the tenant ID to search the corresponding tenant users. The default value is empty (search the users of this tenant and the users of the cooperating tenants) |

### Request Example

```
// URL Query Parameters
keyword=zhang
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
            "organization_paths": ["公司/部门A/中心AA"],
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "full_name": "张四",
            "display_name": "张四",
            "data_source_type": "real",
            "owner_tenant_id": "collaborative_tenant",
            "organization_paths": ["公司/部门A/中心AB", "公司/部门B/中心BA"],
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangwu",
            "full_name": "张五",
            "display_name": "张五",
            "data_source_type": "virtual",
            "owner_tenant_id": "default",
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
| organization_paths | array  | The organization paths to which the user belongs, separated by commas, with the format of `Department 1/Department 2/.../Department n`; virtual users have no organization path          |

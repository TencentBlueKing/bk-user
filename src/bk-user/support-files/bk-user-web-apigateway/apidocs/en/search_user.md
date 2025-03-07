### Description

Search user(including collaborative users and virtual users). The search results return the first 100 data by default(If you need more search results, you need to refine the search conditions).

### Parameters

| Name    | Type   | Required | Description                                                                                                        |
|---------|--------|----------|--------------------------------------------------------------------------------------------------------------------|
| keyword | string | No       | Search keywords (you can enter the values of login_name (unique ID of user in the enterprise) or full_name (name)) |

### Request Example

```
// URL Query Parameters
keyword=张
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "bk_username": "hc6n2ydjxtxef4cw",
            "login_name": "zhangsan",
            "display_name": "张三",
            "type": "real",
            "tenant_id": "",
            "tenant_name": ""
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "display_name": "张四",
            "type": "real",
            "tenant_id": "test",
            "tenant_name": "测试协同租户"
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangwu",
            "display_name": "张五",
            "type": "virtual",
            "tenant_id": "",
            "tenant_name": ""
        },
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                                                                          |
|--------------|--------|--------------------------------------------------------------------------------------|
| bk_username  | string | Blueking user's unique identifier                                                    |
| login_name   | string | Unique ID of the user within the enterprise                                          |
| display_name | string | User's display_name                                                                  |
| type         | string | User type, where `real` indicates a real user and `virtual` indicates a virtual user |
| tenant_id    | string | Tenant ID, which is empty for real users and filled for virtual users                |
| tenant_name  | string | Tenant name, which is empty for real users and filled for virtual users              |

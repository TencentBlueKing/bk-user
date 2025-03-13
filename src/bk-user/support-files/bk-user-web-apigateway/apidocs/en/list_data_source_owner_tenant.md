### Description

Get the information of the tenant of all data sources in this tenant (including collaborative tenants)


### Response Example for Status Code 200

```json5
{
  "data": [
    {
      "id": "default",
      "name": "默认租户"
    },
    {
      "id": "collab_tenant_1",
      "name": "协同租户1"
    },
    {
      "id": "collab_tenant_2",
      "name": "协同租户2"
    }
  ]
}
```

### Response Parameters Description

| 参数名称                | 参数类型   | 描述       |
|---------------------|--------|----------|
| id                  | string | 租户 ID    |
| name                | string | 租户名称     |

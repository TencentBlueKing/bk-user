### Description

Get the tenant list of all data sources in this tenant (including collaborative tenants)


### Response Example for Status Code 200

```json5
{
    "data": {
        "id": "default",
        "name": "默认租户",
        "collab_tenants": [
          {
            "id": "collab_tenant_1",
            "name": "协同租户1"
          },
          {
            "id": "collab_tenant_2",
            "name": "协同租户2"
          }
        ],
    }
}
```

### Response Parameters Description

| Name                | Type   | Description                          |
|---------------------|--------|--------------------------------------|
| id                  | string | Tenant ID                            |
| name                | string | Tenant name                          |
| collab_tenants      | array  | Information of Collaborative tenants |

**collab_tenants** is a list of collaborative tenants. Each element in the list contains the information of the collaborative tenant (including tenant ID and tenant name). Each collaborative tenant contains the following parameters:

| Name | Type   | Description                         |
|------|--------|-------------------------------------|
| id   | string | Unique identifier of the department |
| name | string | The name of the department          |

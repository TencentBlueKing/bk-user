### Description

Query the tenant list by pagination

### Parameters

| Name      | Type | Required | Description                             |
|-----------|------|----------|-----------------------------------------|
| page      | int  | No       | page number, default is 1               |
| page_size | int  | No       | number of pages per page, default is 10 |

### Request Example

Example: Use curl to carry the authorization header and tenant header to request:

```shell
curl -X GET -H 'X-Bkapi-Authorization: {"bk_app_code": "x", "bk_app_secret": "y"}' -H 'X-Bk-Tenant-Id: your_app_tenant_id' "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/?page=1&page_size=10"
```

Example: Use Python and the **requests** module:

``` python
import json
import requests

result = requests.get(
    "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/",
    headers={
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": "x", "bk_app_secret": "y"}),
        "X-Bk-Tenant-Id": "your_app_tenant_id"
    },
    params={
        "page": 1,
        "page_size": 10
    },
)
```

### Response Example

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": "default",
        "name": "Default",
        "status": "enabled"
      },
      {
        "id": "test",
        "name": "Test",
        "status": "disabled"
      }
    ]
  }
}
```

### Response Parameters Description

| Name   | Type   | Description                                                |
|--------|--------|------------------------------------------------------------|
| count  | int    | the total number of tenants                                |
| id     | string | tenant ID                                                  |
| name   | string | the name of tenant                                         |
| status | string | the status of tenant, which can be `enabled` or `disabled` |

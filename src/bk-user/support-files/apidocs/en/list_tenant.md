### Description

Query the list of tenants

### Parameters

No parameters

### Request Example

Example: Use curl to carry the authorization header:
```shell
curl -X GET -H 'X-Bkapi-Authorization: {"bk_app_code": "x", "bk_app_secret": "y"}' "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/"
```
Example: Use Python and the **requests** module:
``` python
import json
import requests

result = requests.get(
    "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/"
    headers={
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": "x", "bk_app_secret": "y"})
    },
)
```

### Response Example

```json5
{
  "data":
    [
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
```

### Response Parameters Description

| Name | Type | Description                                                |
|------|------|------------------------------------------------------------|
| id   | string | tenant ID                                                  |
| name | string | the name of tenant                                         |
| status | string | the status of tenant, which can be `enabled` or `disabled` |

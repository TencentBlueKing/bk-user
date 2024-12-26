### Description

Query the list of tenants

### Parameters

The interface is a paging interface, which supports the input of page and page_size parameters, which represent the
number of pages and the number of pages per page respectively. If not input, the default is page=1, page_size=10.

| Name      | Type | Required | Description                             |
|-----------|------|----------|-----------------------------------------|
| page      | int  | No       | page number, default is 1               |
| page_size | int  | No       | number of pages per page, default is 10 |

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
  "data": [
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

| Name   | Type   | Description                                                |
|--------|--------|------------------------------------------------------------|
| id     | string | tenant ID                                                  |
| name   | string | the name of tenant                                         |
| status | string | the status of tenant, which can be `enabled` or `disabled` |

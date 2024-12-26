### Description

Query user's information corresponding to bk_token

### Parameters

| Name     | Type   | Required | Description                                                       |
|----------|--------|----------|-------------------------------------------------------------------|
| bk_token | string | Yes      | User login state ticket, which needs to be retrieved from Cookies |

### Request Example

Example: Use curl to carry the authorization header and tenant header to request:

```shell
curl -X GET -H 'X-Bkapi-Authorization: {"bk_app_code": "x", "bk_app_secret": "y"}' -H 'X-Bk-Tenant-Id: your_app_tenant_id' "https://bkapi.example.com/api/bk-login/prod/login/api/v3/open/bk-tokens/userinfo/?bk_token=bkcrypt%24gAAAAABnWEIbW4BC9VrczvN5pE-ga9fjq0JvT-ZbbjRRIYeVpGsRWWR3NASAzEDHGvPSjshkK-lqgUnqkDSNao58xTrbtCrDIQFrPlDmKXfXPvu2aLOVGz1mrzftygyAEHQ0G1HFXEexfn3CjkwedW5j2-Yu-GU5XA%3D%3D"
```

Example: Use Python and the **requests** module:

``` python
import json
import requests

result = requests.get(
    "https://bkapi.example.com/api/bk-login/prod/login/api/v3/open/bk-tokens/userinfo/",
    headers={
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": "x", "bk_app_secret": "y"}),
        "X-Bk-Tenant-Id": "your_app_tenant_id"
    },
    params={
        "bk_token": "bkcrypt%24gAAAAABnWEIbW4BC9VrczvN5pE-ga9fjq0JvT-ZbbjRRIYeVpGsRWWR3NASAzEDHGvPSjshkK-lqgUnqkDSNao58xTrbtCrDIQFrPlDmKXfXPvu2aLOVGz1mrzftygyAEHQ0G1HFXEexfn3CjkwedW5j2-Yu-GU5XA%3D%3D"},
)
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "bk_username": "nteuuhzxlh0jcanw",
    "tenant_id": "system",
    "display_name": "admin",
    "language": "zh-cn",
    "time_zone": "Asia/Shanghai"
  }
}

```

### Response Parameters Description

| Name         | Type   | Description                                  |
|--------------|--------|----------------------------------------------|
| bk_username  | string | User unique identifier, globally unique      |
| tenant_id    | string | User's tenant ID                             |
| display_name | string | User display name                            |
| language     | string | User language, enumerated values: zh-cn / en |
| time_zone    | string | User's time zone                             |

### Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Login session has expired"
  }
}
```

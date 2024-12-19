### Description

Query user's information corresponding to bk_token

### Input Parameters

| Parameter Name | Parameter Type | Required | Description                                                                                     |
|----------------|----------------|----------|-------------------------------------------------------------------------------------------------|
| bk_token       | string         | Yes      | bkcrypt%24gAAAAABnWEIbW4BC9VrczvN5pE-ga9fjq0JvT-ZbbjRRIYeVpGsRWWR3NASAzEDHGvPSjshkK-lqgUnqkDSNao58xTrbtCrDIQFrPlDmKXfXPvu2aLOVGz1mrzftygyAEHQ0G1HFXEexfn3CjkwedW5j2-Yu-GU5XA%3D%3D |


### Example Response for Status Code 200

```json
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

### Response Parameter Description

| Parameter Name  | Parameter Type | Description                                         |
|------------------|----------------|-----------------------------------------------------|
| bk_username       | string         | User unique identifier, globally unique             |
| tenant_id         | string         | User's tenant ID                                   |
| display_name      | string         | User display name                                   |
| language          | string         | User language, enumerated values: zh-cn / en      |
| time_zone         | string         | User's time zone                                   |

### Example Response for Non-200 Status Code

```json
// status_code = 400
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Login session has expired"
    }
}
```

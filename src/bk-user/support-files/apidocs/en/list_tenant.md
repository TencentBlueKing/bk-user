### Description

Query the tenant list by pagination

### Parameters

| Name      | Type | Required | Description                             |
|-----------|------|----------|-----------------------------------------|
| page      | int  | No       | page number, default is 1               |
| page_size | int  | No       | number of pages per page, default is 10 |

### Request Example

// URL Query Parameters
page=1&page_size=10

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

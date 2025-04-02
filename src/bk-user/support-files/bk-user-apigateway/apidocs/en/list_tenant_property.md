### Description

(Pagination) Query the list of the common properties of the tenant.

### Parameters

| Name      | Type | Required | Description                                                 |
|-----------|------|----------|-------------------------------------------------------------|
| page      | int  | No       | Page number, default is 1                                   |
| page_size | int  | No       | The number of pages per page, default is 10, maximum is 500 |

### Request Example

```
// URL Query Parameters
page=1&page_size=5
```

### Response Example

```json5
{
    "data": {
        "count": 2,
        "results": [
            {
                "key": "key_1",
                "value": "value_1",
            },
            {
                "key": "key_2",
                "value": "value_2",
            }
        ]
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                      |
|--------------|--------|----------------------------------|
| key          | string | The name of the common property  |
| value        | string | The value of the common property |

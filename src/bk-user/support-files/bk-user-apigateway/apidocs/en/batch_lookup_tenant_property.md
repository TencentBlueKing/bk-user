### Description

Batch query the common properties of the tenant

### Parameters

| Name         | Type   | Required | Description                                                                                                                        |
|--------------|--------|----------|------------------------------------------------------------------------------------------------------------------------------------|
| lookups      | string | Yes      | The name of property for exact lookup, multiple separated by separator, limit number is 100, maximum input length per value is 255 |

### Request Example

```
// URL Query Parameter
lookups=key_1,key_2
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "key": "key_1",
            "value": "value_1",
        },
        {
            "key": "key_2",
            "value": "value_2"
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                      |
|--------------|--------|----------------------------------|
| key          | string | The name of the common property  |
| value        | string | The value of the common property |

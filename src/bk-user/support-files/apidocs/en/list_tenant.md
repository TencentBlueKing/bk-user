### Description

Query the tenant list

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

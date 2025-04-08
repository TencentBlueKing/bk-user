### Description

Query the list of common variables of the tenant

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "name": "name_1",
            "value": "value_1",
        },
        {
            "name": "name_2",
            "value": "value_2"
        }
    ]
}
```

### Response Parameters Description

| Name  | Type   | Description                      |
|-------|--------|----------------------------------|
| name  | string | The name of the common variable  |
| value | string | The value of the common variable |

### Description

Query the list of tenant user's custom enum fields

### Parameters

| Name  | Type   | Required | Description                                                                       |
|-------|--------|----------|-----------------------------------------------------------------------------------|
| names | string | No       | The English identifier of the field, multiple identifiers are separated by commas |

### Request Example

```
// URL Query Parameters
names=enum_field,multi_enum_field
```

### Response Example for Status Code 200

```json5
{
    "data": [
        {
            "name": "enum_field",
            "display_name": "枚举字段",
            "data_type": "enum",
            "options": [
              {"id": "1", "value": "选项1"},
              {"id": "2", "value": "选项2"}
            ]
        },
        {
            "name": "multi_enum_field",
            "display_name": "多枚举字段",
            "data_type": "multi_enum",
            "options": [
              {"id": "3", "value": "选项3"},
              {"id": "4", "value": "选项4"}
            ]
        }
    ]
}
```

### Response Parameters Description

| Name         | Type   | Description                                    |
|--------------|--------|------------------------------------------------|
| name         | string | The English sign of the field                  |
| display_name | string | The name of the field                          |
| data_type    | string | The type of the field（`enum` and `multi_enum`） |
| options      | array  | The options of the field                       |

Each dict element in the options list consists of the following fields:

| Name  | Type   | Description           |
|-------|--------|-----------------------|
| id    | string | The ID of the enum    |
| value | string | The value of the enum |

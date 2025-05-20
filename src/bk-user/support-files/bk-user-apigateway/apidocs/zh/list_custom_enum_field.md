### 描述

查询租户用户枚举字段信息列表

### 响应示例

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

### 响应参数说明

| 参数名称         | 参数类型   | 描述                                |
|--------------|--------|-----------------------------------|
| name         | string | 字段英文标识                            |
| display_name | string | 字段名称                              |
| data_type    | string | 字段类型（枚举 `enum` 与多枚举 `multi_enum`） |
| options      | array  | 枚举选项                              |

options 列表中的每个字典元素由以下字段组成：

| 参数名称  | 参数类型   | 描述    |
|-------|--------|-------|
| id    | string | 枚举 ID |
| value | string | 枚举值   |

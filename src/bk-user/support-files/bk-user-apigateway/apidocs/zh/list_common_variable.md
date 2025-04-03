### 描述

查询租户公共变量信息列表

### 响应示例

```json5
{
    "data": [
        {
            "name": "key_1",
            "value": "value_1",
        },
        {
            "name": "key_2",
            "value": "value_2"
        }
    ]
}
```

### 响应参数说明

| 参数名称  | 参数类型   | 描述    |
|-------|--------|-------|
| name  | string | 公共变量名 |
| value | string | 公共变量值 |

### 描述

（分页）查询虚拟用户列表

### 状态码 200 的响应示例

```json5
{
    "data": {
        "count": 2,
        "results": [
             {
                "bk_username": "klzwge6k69ly0rjt",
                "login_name": "virtual_user_1",
                "display_name": "虚拟用户1"
             },
             {
                "bk_username": "soxteugr5ymfi3w1",
                "login_name": "virtual_user_2",
                "display_name": "虚拟用户2"
            }
        ]
    }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述        |
|--------------|--------|-----------|
| bk_username  | string | 蓝鲸用户唯一标识  |
| login_name   | string | 企业内用户唯一标识 |
| display_name | string | 用户展示名     |

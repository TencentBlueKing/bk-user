### 描述

搜索虚拟用户，搜索结果默认返回前 100 条数据（如需更多搜索结果，需要细化搜索条件）

### 输入参数

| 参数名称    | 参数类型   | 必选 | 描述                                                         |
|---------|--------|----|------------------------------------------------------------|
| keyword | string | 是  | 搜索关键字（可输入 login_name 或者 full_name 的值），至少输入长度为 1，至多输入长度为 64 |

### 请求示例

```
// URL Query 参数
keyword=zhang
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "klzwge6k69ly0rjt",
            "login_name": "virtual_user_1",
            "full_name": "虚拟用户1",
            "display_name": "virtual_user_1(虚拟用户1)",
            "status": "enabled"
        },
        {
            "bk_username": "soxteugr5ymfi3w1",
            "login_name": "virtual_user_2",
            "full_name": "虚拟用户2",
            "display_name": "virtual_user_2(虚拟用户2)",
            "status": "enabled"
        }
    ]
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述                                                                      |
|--------------|--------|-------------------------------------------------------------------------|
| bk_username  | string | 蓝鲸用户唯一标识                                                                |
| login_name   | string | 企业内用户唯一标识                                                               |
| full_name    | string | 用户姓名                                                                    |
| display_name | string | 用户展示名                                                                   |
| status       | string | 用户状态，其中 `enabled` 表示**启用**状态；`disabled` 表示**禁用**状态；`expired` 表示**过期**状态 |

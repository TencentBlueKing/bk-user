### 描述

批量查询实名用户信息

### 参数说明

| 参数名称         | 参数类型   | 必选 | 描述                                                                 |
|--------------|--------|----|--------------------------------------------------------------------|
| lookups      | string | 是  | 精确查询的值（可以为 bk_username、login_name），多个以逗号分隔，限制数量为 100，每个值最大输入长度为 64 |
| lookup_field | string | 是  | 查询字段，可选值为 `bk_username`、`login_name`                               |

### 请求示例

```
// URL Query 参数
lookups=zhangsan,lisi&lookup_field=login_name
```

### 200 状态码响应示例

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "display_name": "zhangsan(张三)",
            "status": "enabled"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
            "display_name": "lisi(李四)",
            "status": "enabled"
        }
    ]
}
```

### 响应参数说明

| 参数名          | 类型     | 说明                                                                      |
|--------------|--------|-------------------------------------------------------------------------|
| bk_username  | string | 蓝鲸用户唯一标识                                                                |
| login_name   | string | 企业内用户唯一标识（登录名）                                                          |
| display_name | string | 用户展示名                                                                   |
| status       | string | 用户状态，其中 `enabled` 表示**启用**状态；`disabled` 表示**禁用**状态；`expired` 表示**过期**状态 |

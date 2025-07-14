### 描述

批量查询实名用户信息

### 参数说明

| 参数名         | 类型     | 是否必填 | 说明                                 |
|-------------|--------|------|------------------------------------|
| login_names | string | 是    | 用户登录名，多个用英文逗号分隔，最多 100 个，单个最大长度 64 |

### 请求示例

```
// URL 查询参数
login_names=zhangsan,lisi
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

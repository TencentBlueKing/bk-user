### 描述

查询用户信息

### 输入参数

| 参数名称        | 参数类型   | 必选 | 描述       |
|-------------|--------|----|----------|
| bk_username | string | 是  | 蓝鲸用户唯一标识 |

### 请求示例

```
// URL Path 参数
/api/open/v3/tenant/users/7idwx3b7nzk6xigs/
```

### 状态码 200 的响应示例

```json5
{
    "data": {
        "tenant_id": "default",
        "bk_username": "7idwx3b7nzk6xigs",
        "login_name": "zhangsan",
        "display_name": "zhangsan(张三)",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
        "status": "enabled"
    }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述                                                                      |
|--------------|--------|-------------------------------------------------------------------------|
| tenant_id    | string | 租户 ID                                                                   |
| bk_username  | string | 蓝鲸用户唯一标识                                                                |
| login_name   | string | 企业内用户唯一标识                                                               |
| display_name | string | 用户展示名                                                                   |
| time_zone    | string | 时区                                                                      |
| language     | string | 语言                                                                      |
| status       | string | 用户状态，其中 `enabled` 表示**启用**状态；`disabled` 表示**禁用**状态；`expired` 表示**过期**状态 |

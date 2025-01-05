### 描述

查询用户详情

### 输入参数

| 参数名称        | 参数类型   | 必选 | 描述       |
|-------------|--------|----|----------|
| bk_username | string | 是  | 蓝鲸用户唯一标识 |

### 请求示例

```
// URL Path 参数
/api/open/v3/tenant/users/{bk_username}/
```

### 状态码 200 的响应示例

```json5
{
  "data": {
    "tenant_id": "default",
    "bk_username": "7idwx3b7nzk6xigs",
    "display_name": "张三",
    "time_zone": "Asia/Shanghai",
    "language": "zh-cn",
  }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| tenant_id    | string | 租户 ID    |
| bk_username  | string | 蓝鲸用户唯一标识 |
| display_name | string | 用户展示名    |
| time_zone    | string | 时区       |
| language     | string | 语言       |

### 状态码非 200 的响应示例

```json5
// status_code = 404
{
  "error": {
    "code": "NOT_FOUND",
    "message": "对象未找到"
  }
}
```

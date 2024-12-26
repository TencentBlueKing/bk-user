### 描述

查询 bk_token 对应的用户信息

### 输入参数

| 参数名称     | 参数类型   | 必选 | 描述                      |
|----------|--------|----|-------------------------|
| bk_token | string | 是  | 用户登录态票据，需要从 Cookies 中获取 |

### 调用示例

// URL Query 参数
bk_token=bkcrypt%24gAAAAABnWEIbW4BC9VrczvN5pE-ga9fjq0JvT-ZbbjRRIYeVpGsRWWR3NASAzEDHGvPSjshkK-lqgUnqkDSNao58xTrbtCrDIQFrPlDmKXfXPvu2aLOVGz1mrzftygyAEHQ0G1HFXEexfn3CjkwedW5j2-Yu-GU5XA%3D%3D

### 状态码 200 的响应示例

```json5
{
  "data": {
    "bk_username": "nteuuhzxlh0jcanw",
    "tenant_id": "system",
    "display_name": "admin",
    "language": "zh-cn",
    "time_zone": "Asia/Shanghai"
  }
}

```

### 响应参数说明

| 参数名称         | 参数类型   | 描述                  |
|--------------|--------|---------------------|
| bk_username  | string | 用户唯一标识，全局唯一         |
| tenant_id    | string | 用户所属租户 ID           |
| display_name | string | 用户展示名               |
| language     | string | 用户语言，枚举值：zh-cn / en |
| time_zone    | string | 用户所在时区              |

### 状态码 非 200 的响应示例

```json5
// status_code = 400
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "登录态已过期"
  }
}
```

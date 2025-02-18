### 描述

查询用户展示信息

### 输入参数

| 参数名称    | 参数类型 | 必选 | 描述             |
| ----------- | -------- | ---- | ---------------- |
| bk_username | string   | 是   | 蓝鲸用户唯一标识 |

### 请求示例

```
// URL Path 参数
/api/v3/open-web/tenant/users/7idwx3b7nzk6xigs/display_info
```

### 状态码 200 的响应示例

```json5
{
    "data": {
        "display_name": "张三"
    }
}
```


### 响应参数说明

| 参数名称     | 参数类型 | 描述       |
| ------------ | -------- | ---------- |
| display_name | string   | 用户展示名 |

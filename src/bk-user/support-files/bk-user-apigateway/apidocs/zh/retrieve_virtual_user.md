### 描述

查询虚拟用户信息

### 输入参数

| 参数名称       | 参数类型   | 必选 | 参数位置        | 描述                 |
|------------|--------|----|-------------|--------------------|
| login_name | string | 是  | path        | 部门唯一标识             |

### 请求示例

```
// URL Path 参数
/api/v3/open/tenant/virtual-users/bk_admin/
```

### 状态码 200 的响应示例

```json5
{
    "data": {
        "bk_username": "7idwx3b7nzk6xigs",
        "display_name": "bk_admin"
    }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| bk_username  | string | 蓝鲸用户唯一标识 |
| display_name | string | 用户展示名    |

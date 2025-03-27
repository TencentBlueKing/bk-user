### 描述

（分页）查询虚拟用户信息列表

### 输入参数

| 参数名称       | 参数类型   | 必选 | 描述                 |
|------------|--------|----|--------------------|
| login_name | string | 否  | 企业内用户唯一标识          |
| page       | int    | 否  | 页码，从 1 开始          |
| page_size  | int    | 否  | 每页数量，默认为 10，最大 500 |

### 请求示例

```
// URL Query 参数
login_name=bk_admin&page=1&page_size=5
```

### 状态码 200 的响应示例

```json5
{
    "data": {
        "count": 1,
        "results": [
            {
                "bk_username": "q9k6bhqks0ckl5ew",
                "login_name": "bk_admin",
                "display_name": "bk_admin"
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

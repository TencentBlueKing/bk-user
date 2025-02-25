### 描述

批量查询用户展示名

### 输入参数

| 参数名称         | 参数类型   | 必选 | 描述                         |
|--------------|--------|----|----------------------------|
| bk_usernames | string | 是  | 蓝鲸用户唯一标识，多个以逗号分隔，限制数量为 100 |

### 请求示例

```
// URL Query 参数
bk_usernames=7idwx3b7nzk6xigs,0wngfim3uzhadh1w
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "display_name": "张三"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "display_name": "李四"
        }
    ]
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| bk_username  | string | 蓝鲸用户唯一标识 |
| display_name | string | 用户展示名    |

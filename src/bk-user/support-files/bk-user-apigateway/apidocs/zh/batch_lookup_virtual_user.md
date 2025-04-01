### 描述

批量查询虚拟用户信息

### 输入参数

| 参数名称         | 参数类型   | 必选 | 描述                                                                 |
|--------------|--------|----|--------------------------------------------------------------------|
| lookups      | string | 是  | 精确查询的值（可以为 bk_username、login_name），多个以逗号分隔，限制数量为 100，每个值最大输入长度为 64 |
| lookup_field | string | 是  | 查询字段，可选值为 `bk_username`、`login_name`                               |

### 请求示例

```
// URL Query 参数
lookups=zhangsan,lisi&lookup_field=login_name
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "display_name": "zhangsan(张三)"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
            "display_name": "lisi(李四)"
        }
    ]
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述        |
|--------------|--------|-----------|
| bk_username  | string | 蓝鲸用户唯一标识  |
| login_name   | string | 企业内用户唯一标识 |
| display_name | string | 用户展示名     |

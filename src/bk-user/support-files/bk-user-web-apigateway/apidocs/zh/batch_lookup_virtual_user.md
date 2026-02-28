### 描述

批量精确查询虚拟用户

### 输入参数

| 参数名称          | 参数类型   | 必选 | 描述                                                                                        |
|---------------|--------|----|-------------------------------------------------------------------------------------------|
| lookups       | string | 是  | 精确匹配的值（可以为 bk_username、login_name 或 full_name），多个以逗号分隔，限制数量为 100，每个值最大输入长度为 64 |
| lookup_fields | string | 是  | 匹配字段，多个以逗号分隔，每个元素可选值为`bk_username`、`login_name`、`full_name`                    |

### 请求示例

```
// URL Query 参数
lookups=zhangsan,lisi&lookup_fields=login_name,bk_username
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "7idwx3b7nzk6xigs",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)"
        },
        {
            "bk_username": "0wngfim3uzhadh1w",
            "login_name": "lisi",
            "full_name": "李四",
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
| full_name    | string | 用户姓名      |
| display_name | string | 用户展示名     |

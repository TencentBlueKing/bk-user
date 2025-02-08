### 描述

查询用户 Leader 列表

### 输入参数

| 参数名称           | 参数类型    | 必选 | 描述                 |
|----------------|---------|----|--------------------|
| bk_username    | string  | 是  | 蓝鲸用户唯一标识           |

### 请求示例

```
// URL Path 参数
/api/v3/open/tenant/users/mzmwjffhhbjg4fxz/leaders/
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "q9k6bhqks0ckl5ew",
            "display_name": "张三"
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "display_name": "李四"
        }
    ]
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| bk_username  | string | 蓝鲸用户唯一标识 |
| display_name | string | 用户展示名称   |

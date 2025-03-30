### 描述

（分页）根据部门 ID 查询部门下的用户列表

### 输入参数

| 参数名称          | 参数类型 | 必选 | 参数位置        | 描述                 |
|---------------|------|----|-------------|--------------------|
| page          | int  | 否  | query param | 页码，从 1 开始          |
| page_size     | int  | 否  | query param | 每页数量，默认为 10，最大 500 |
| department_id | int  | 是  | path        | 部门唯一标识             |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open/tenant/departments/2/users/?page=1&page_size=5
```

### 状态码 200 的响应示例

```json5
{
    "data": {
        "count": 2,
        "results": [
            {
                "bk_username": "q9k6bhqks0ckl5ew",
                "full_name": "张三",
                "display_name": "zhangsan(张三)"
            },
            {
                "bk_username": "er0ugcammqwf1q5w",
                "full_name": "李四",
                "display_name": "lisi(李四)"
            }
        ]
    }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| bk_username  | string | 蓝鲸用户唯一标识 |
| full_name    | string | 用户姓名     |
| display_name | string | 用户展示名    |

### 描述

批量创建用户（数据提供方专用接口）

### 路径参数

| 参数名称          | 参数类型 | 必选 | 描述      |
|---------------|------|----|---------|
| data_source_id | int  | 是  | 数据源 ID |

### 请求参数

| 参数名称             | 参数类型   | 必选 | 描述                   |
|------------------|--------|----|-----------------------|
| users            | array  | 是  | 用户列表，最大 100 条        |
| users[].id       | string | 是  | 用户唯一标识（数据源内）         |
| users[].username | string | 是  | 用户名                  |
| users[].full_name | string | 是  | 姓名                   |
| users[].email    | string | 否  | 邮箱                   |
| users[].phone    | string | 否  | 手机号                  |
| users[].phone_country_code | string | 否  | 手机国际区号，默认 86 |
| users[].extras   | object | 否  | 自定义字段                |

### 请求示例

```json
{
    "users": [
        {
            "id": "emp_001",
            "username": "zhangsan",
            "full_name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "phone_country_code": "86",
            "extras": {}
        }
    ]
}
```

### 响应示例

```
HTTP 201 Created
```

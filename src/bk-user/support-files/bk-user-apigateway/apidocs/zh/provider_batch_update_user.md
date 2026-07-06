### 描述

批量更新用户（数据提供方专用接口）

### 路径参数

| 参数名称          | 参数类型 | 必选 | 描述      |
|---------------|------|----|---------|
| data_source_id | int  | 是  | 数据源 ID |

### 请求参数

| 参数名称                       | 参数类型   | 必选 | 描述              |
|----------------------------|--------|----|-----------------|
| users                      | array  | 是  | 用户列表，最大 100 条   |
| users[].id                 | string | 是  | 用户唯一标识（数据源内）   |
| users[].username           | string | 否  | 用户名             |
| users[].full_name          | string | 否  | 姓名              |
| users[].email              | string | 否  | 邮箱              |
| users[].phone              | string | 否  | 手机号             |
| users[].phone_country_code | string | 否  | 手机国际区号          |
| users[].extras             | object | 否  | 自定义字段           |

### 请求示例

```json
{
    "users": [
        {
            "id": "emp_001",
            "full_name": "张三(更新)",
            "email": "new@example.com"
        }
    ]
}
```

### 响应示例

```
HTTP 204 No Content
```

### 描述

根据部门 ID 查询部门下的用户列表

### 输入参数

| 参数名称            | 参数类型   | 必选 | 参数位置        | 描述                                      |
|-----------------|--------|----|-------------|-----------------------------------------|
| department_id   | int    | 是  | path        | 部门唯一标识（值为 0 默认返回无部门用户）                  |
| owner_tenant_id | string | 否  | query_param | 数据源所属租户 ID，若 department_id 为 0，则必须传入该参数 |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open-web/tenant/departments/1/users/
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "q9k6bhqks0ckl5ew",
            "login_name": "zhangsan",
            "display_name": "张三"
        },
        {
            "bk_username": "er0ugcammqwf1q5w",
            "login_name": "lisi",
            "display_name": "李四"
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

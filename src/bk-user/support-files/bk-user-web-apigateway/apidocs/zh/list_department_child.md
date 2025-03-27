### 描述

获取部门的子部门（包括协同）列表

### 输入参数

| 参数名称                 | 参数类型   | 必选 | 参数位置        | 描述                                      |
|----------------------|--------|----|-------------|-----------------------------------------|
| parent_department_id | int    | 是  | path        | 部门 ID（为 0 则默认获取根部门）                     |
| owner_tenant_id      | string | 否  | query_param | 数据源所属租户 ID，若 department_id 为 0，则必须传入该参数 |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open-web/tenant/departments/1/children/
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "has_child": true,
            "has_user": true
        },
        {
            "id": 5,
            "name": "中心AB",
            "has_child": false,
            "has_user": true
        }
    ]
}
```

### 响应参数说明

| 参数名称      | 参数类型   | 描述     |
|-----------|--------|--------|
| id        | int    | 部门唯一标识 |
| name      | string | 部门名称   |
| has_child | bool   | 是否有子部门 |
| has_user  | bool   | 是否有用户  |

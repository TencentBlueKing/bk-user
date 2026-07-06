### 描述

批量创建用户-部门关系（数据提供方专用接口）

### 路径参数

| 参数名称          | 参数类型 | 必选 | 描述      |
|---------------|------|----|---------|
| data_source_id | int  | 是  | 数据源 ID |

### 请求参数

| 参数名称                       | 参数类型   | 必选 | 描述              |
|----------------------------|--------|----|-----------------|
| relations                  | array  | 是  | 关系列表，最大 100 条   |
| relations[].user_id        | string | 是  | 用户唯一标识（数据源内）   |
| relations[].department_id  | string | 是  | 部门唯一标识（数据源内）   |

### 请求示例

```json
{
    "relations": [
        {"user_id": "emp_001", "department_id": "dept_a"},
        {"user_id": "emp_002", "department_id": "dept_b"}
    ]
}
```

### 响应示例

```
HTTP 204 No Content
```

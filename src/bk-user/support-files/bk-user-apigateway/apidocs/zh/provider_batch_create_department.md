### 描述

批量创建部门（数据提供方专用接口）

注意：部门创建后默认为根部门，父子关系通过 `department-relations` 接口单独设置。

### 路径参数

| 参数名称          | 参数类型 | 必选 | 描述      |
|---------------|------|----|---------|
| data_source_id | int  | 是  | 数据源 ID |

### 请求参数

| 参数名称               | 参数类型   | 必选 | 描述                |
|--------------------|--------|----|--------------------|
| departments        | array  | 是  | 部门列表，最大 100 条     |
| departments[].id   | string | 是  | 部门唯一标识（数据源内）     |
| departments[].name | string | 是  | 部门名称              |

### 请求示例

```json
{
    "departments": [
        {"id": "company", "name": "总公司"},
        {"id": "dept_a", "name": "部门A"}
    ]
}
```

### 响应示例

```
HTTP 201 Created
```

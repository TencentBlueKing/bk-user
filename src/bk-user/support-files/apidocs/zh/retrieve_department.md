### 描述

查询部门信息（支持是否包括祖先部门）

### 输入参数

| 参数名称 | 参数类型 | 必选 | 参数位置｜描述 |
|----------------|---------|----|--------｜--------------------|
| department_id | int | 是 | path |租户部门 ID |
| with_ancestors | boolean | 否 | query param | 是否包括祖先部门，默认为 false |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open/tenant/departments/3/?with_ancestors=true
```

### 状态码 200 的响应示例

```json5
{
  "id": 3,
  "name": "部门C",
  "ancestors": [
    {
      "id": 1,
      "name": "部门A"
    },
    {
      "id": 2,
      "name": "部门B"
    }
  ]
}
```

### 响应参数说明

| 参数名称      | 参数类型   | 描述      |
|-----------|--------|---------|
| id        | int    | 租户部门 ID |
| name      | string | 租户部门名称  |
| ancestors | list   | 祖先部门列表  |

#### ancestors 参数说明

**ancestors** 为祖先部门列表，列表中的每个元素为用户部门的祖先部门信息，默认以降序排列（从根祖先部门 -> 父部门），例如：若用户部门为
**小组AAA**，父部门为**中心AA**，那么祖先部门列表中的顺序可以为`公司 -> 部门A -> 中心AA`。每个祖先部门包含以下参数：

| 参数名称 | 参数类型   | 描述      |
|------|--------|---------|
| id   | int    | 祖先部门 ID |
| name | string | 祖先部门名称  |

### 状态码非 200 的响应示例

```json5
// status_code = 404
{
  "error": {
    "code": "NOT_FOUND",
    "message": "对象未找到"
  }
}
```

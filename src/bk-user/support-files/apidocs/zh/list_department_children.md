### 描述

（分页）根据部门 ID 查询子部门列表，支持按照层级 Level 递归查询

### 输入参数

| 参数名称          | 参数类型 | 必选 | 参数位置        | 描述                             |
|---------------|------|----|-------------|--------------------------------|
| page          | int  | 否  | query param | 页码，从 1 开始                      |
| page_size     | int  | 否  | query param | 每页数量，默认为 10                    |
| department_id | int  | 是  | path        | 部门唯一标识                         |
| level         | int  | 否  | query_param | 递归子部门的相对 Level 层级，默认为 1，即直接子部门 |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open/tenant/departments/2/childrens/?level=2&page=1&page_size=5
```

### 状态码 200 的响应示例

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": 6,
        "name": "小组AAA",
      },
      {
        "id": 7,
        "name": "小组ABA",
      }
    ],
  }
}
```

### 响应参数说明

| 参数名称 | 参数类型   | 描述     |
|------|--------|--------|
| id   | int    | 部门唯一标识 |
| name | string | 部门名称   |

例如：部门A的子部门为中心AA、中心AB，中心AA的子部门为小组AAA，中心AB的子部门为小组ABA，则部门A的相对层级 level 为 2
的子部门为：小组AAA -> 小组ABA

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

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "参数校验不通过: level: level 必须大于等于 1"
  }
}
```

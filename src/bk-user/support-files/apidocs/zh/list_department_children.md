### 描述

（分页）根据部门 ID 查询子部门列表

### 输入参数

| 参数名称          | 参数类型 | 必选 | 参数位置        | 描述                 |
|---------------|------|----|-------------|--------------------|
| page          | int  | 否  | query param | 页码，从 1 开始          |
| page_size     | int  | 否  | query param | 每页数量，默认 10         |
| department_id | int  | 是  | path        | 部门唯一标识             |
| is_recursive  | bool | 否  | query_param | 是否递归查询子部门，默认 false |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open/tenant/departments/2/childrens/?is_recursive=true&page=1&page_size=5
```

### 状态码 200 的响应示例

```json5
{
  "data": {
    "count": 4,
    "results": [
      {
        "id": 4,
        "name": "中心AA",
      },
      {
        "id": 6,
        "name": "小组AAA",
      },
      {
        "id": 5,
        "name": "中心AB",
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

若 ***is_recursive*** 为 true，则按层级 Level 递归返回所有子部门。例如：部门A的子部门为中心AA、中心AB，中心AA的子部门为小组AAA，中心AB
的子部门为小组ABA，则部门A的子部门列表返回的顺序为：中心AA -> 小组AAA -> 中心AB -> 小组ABA


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

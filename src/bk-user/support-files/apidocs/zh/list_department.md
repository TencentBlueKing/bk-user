### 描述

（分页）查询部门列表

### 输入参数

| 参数名称      | 参数类型 | 必选 | 描述                        |
|-----------|------|----|---------------------------|
| page      | int  | 否  | 页码，从 1 开始                 |
| page_size | int  | 否  | 每页数量，默认 10                |
| parent_id | int  | 否  | 父部门 ID，精确查询参数，若不传入则查询所有部门 |

### 请求示例

```
// URL Query 参数
page=1&page_size=5&parent_id=1
```

### 状态码 200 的响应示例

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": 2,
        "name": "部门A",
        "parent_id": 1,
      },
      {
        "id": 3,
        "name": "部门B",
        "parent_id": 1,
      }
    ],
  }
}
```

### 响应参数说明

| 参数名称      | 参数类型   | 描述     |
|-----------|--------|--------|
| id        | int    | 部门唯一标识 |
| name      | string | 部门名称   |
| parent_id | int    | 父部门 ID |

### 状态码非 200 的响应示例

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "参数校验不通过: parent_id: 指定的父部门在当前租户中不存在"
  }
}
```

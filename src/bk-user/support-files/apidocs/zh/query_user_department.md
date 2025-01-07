### 描述

查询用户部门信息（支持是否包括祖先部门）

### 输入参数

| 参数名称           | 参数类型    | 必选 | 描述                 |
|----------------|---------|----|--------------------|
| bk_username    | string  | 是  | 蓝鲸唯一标识             |
| with_ancestors | boolean | 否  | 是否包括祖先部门，默认为 false |

### 请求示例

```
// URL Path & Query 参数
/api/v3/open/tenant/users/mzmwjffhhbjg4fxz/departments/?with_ancestors=true
```

### 状态码 200 的响应示例

```json5
{
  "data": [
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
    },
    {
      "id": 6,
      "name": "部门F",
      "ancestors": [
        {
          "id": 1,
          "name": "部门A"
        },
        {
          "id": 4,
          "name": "部门D"
        },
        {
          "id": 5,
          "name": "部门E"
        }
      ]
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

ancestors 为祖先部门列表，列表中的每个元素为对应部门的祖先部门信息，以降序排列（从根祖先部门 -> 直接祖先部门），每个元素包含以下参数：

| 参数名称 | 参数类型   | 描述      |
|------|--------|---------|
| id   | int    | 租户部门 ID |
| name | string | 租户部门名称  |

### 状态码非 200 的响应示例

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "无法找到对应租户用户"
  }
}
```

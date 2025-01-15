### 描述

（分页）查询用户列表

### 输入参数

| 参数名称          | 参数类型   | 必选 | 描述                                            |
|---------------|--------|----|-----------------------------------------------|
| lookup_field  | string | 否  | 查询字段（支持 bk_username、display_name、email、phone） |
| exact_lookups | string | 否  | 精确查询字段值列表，以逗号分隔                               |
| fuzzy_lookups | string | 否  | 模糊查询字段值列表，与逗号分隔                               |
| page          | int    | 否  | 页码，从 1 开始                                     |
| page_size     | int    | 否  | 每页数量，默认 10                                    |

***注意***：若同时提供 exact_lookups 与 fuzzy_lookups 字段，则只会使用 exact_lookups 字段进行查询。

### 请求示例

```
// URL Query 参数
lookup_field=bk_username&exact_lookups=q9k6bhqks0ckl5ew,er0ugcammqwf1q5w
```

### 状态码 200 的响应示例

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "tenant_id": "default",
        "bk_username": "q9k6bhqks0ckl5ew",
        "display_name": "张三",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
      },
      {
        "tenant_id": "default",
        "bk_username": "er0ugcammqwf1q5w",
        "display_name": "李四",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
      }
    ],
  }
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述       |
|--------------|--------|----------|
| tenant_id    | string | 租户 ID    |
| bk_username  | string | 蓝鲸用户唯一标识 |
| display_name | string | 用户展示名    |
| time_zone    | string | 时区       |
| language     | string | 语言       |

返回的用户列表根据查询条件按 bk_username 升序排列。若没有查询条件，则返回所有用户列表。

### 状态码非 200 的响应示例

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "参数校验不通过: lookup_field:  xxx 不是合法选项"
  }
}
```

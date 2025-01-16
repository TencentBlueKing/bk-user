### 描述

（分页）查询用户列表

### 输入参数

| 参数名称      | 参数类型 | 必选 | 描述         |
|-----------|------|----|------------|
| page      | int  | 否  | 页码，从 1 开始  |
| page_size | int  | 否  | 每页数量，默认 10 |

### 请求示例

```
// URL Query 参数
page=1&page_size=5
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

### 状态码非 200 的响应示例

暂无

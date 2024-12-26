### 描述

分页查询租户列表

### 输入参数

| 参数名称      | 参数类型 | 必选 | 描述          |
|-----------|------|----|-------------|
| page      | int  | 否  | 页数, 默认为 1   |
| page_size | int  | 否  | 每页数量，默认为 10 |

### 请求示例

```json5
// URL Query 参数
page=1&page_size=10
```

### 响应示例

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "id": "default",
        "name": "Default",
        "status": "enabled"
      },
      {
        "id": "test",
        "name": "Test",
        "status": "disabled"
      }
    ]
  }
}
```

### 响应参数说明

| 参数名称   | 参数类型   | 描述                              |
|--------|--------|---------------------------------|
| count  | int    | 租户总数                            |
| id     | string | 租户 ID                           |
| name   | string | 租户名                             |
| status | string | 租户状态，enabled 表示启用，disabled 表示禁用 |

### 描述

查询租户列表

### 响应示例

```json5
{
  "data": [
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
```

### 响应参数说明

| 参数名称   | 参数类型   | 描述                              |
|--------|--------|---------------------------------|
| id     | string | 租户 ID                           |
| name   | string | 租户名                             |
| status | string | 租户状态，enabled 表示启用，disabled 表示禁用 |

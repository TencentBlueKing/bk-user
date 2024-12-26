### 描述

查询租户列表

### 输入参数

暂无

### 调用示例

示例：使用 curl 命令，请求时携带认证请求头：
```shell
curl -X GET -H 'X-Bkapi-Authorization: {"bk_app_code": "x", "bk_app_secret": "y"}' "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/"
```
示例：使用 Python 语言和 **requests** 模块：
``` python
import json
import requests

result = requests.get(
    "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/"
    headers={
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": "x", "bk_app_secret": "y"})
    },
)
```

### 响应示例

```json5
{
  "data":
    [
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

| 参数名称 | 参数类型 | 描述                              |
|------| -------- |---------------------------------|
| id   | string   | 租户 ID                           |
| name | string   | 租户名                             |
| status | string | 租户状态，enabled 表示启用，disabled 表示禁用 |

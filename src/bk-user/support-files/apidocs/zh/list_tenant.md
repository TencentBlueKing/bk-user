### 描述

分页查询租户列表

### 输入参数

| 参数名称      | 参数类型 | 必选 | 描述          |
|-----------|------|----|-------------|
| page      | int  | 否  | 页数, 默认为 1   |
| page_size | int  | 否  | 每页数量，默认为 10 |

### 调用示例

示例：使用 curl 命令，请求时携带认证请求头：

```shell
curl -X GET -H 'X-Bkapi-Authorization: {"bk_app_code": "x", "bk_app_secret": "y"}' -H 'X-Bk-Tenant-Id: your_app_tenant_id' "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/?page=1&page_size=10"
```

示例：使用 Python 语言和 **requests** 模块：

``` python
import json
import requests

result = requests.get(
    "https://bkapi.example.com/api/bk-user/prod/api/v3/open/tenants/",
    headers={
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": "x", "bk_app_secret": "y"}),
        "X-Bk-Tenant-Id" : "your_app_tenant_id"
    },
    params={
        "page": 1,
        "page_size": 10
    },
)
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
| id     | string | 租户 ID                           |
| name   | string | 租户名                             |
| status | string | 租户状态，enabled 表示启用，disabled 表示禁用 |

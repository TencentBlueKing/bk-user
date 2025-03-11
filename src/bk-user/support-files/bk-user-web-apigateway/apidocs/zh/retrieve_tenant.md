### 描述

查询租户信息（包括协同租户信息）

### 状态码 200 的响应示例

```json5
{
    "data": {
        "id": "default",
        "name": "默认租户",
        "collab_tenants": [
          {
            "id": "collab_tenant_1",
            "name": "协同租户1"
          },
          {
            "id": "collab_tenant_2",
            "name": "协同租户2"
          }
        ],
    }
}
```

### 响应参数说明

| 参数名称                | 参数类型   | 描述       |
|---------------------|--------|----------|
| id                  | string | 租户 ID    |
| name                | string | 租户名称     |
| collab_tenants      | array  | 协同租户信息   |

**collab_tenants** 为协同租户列表，列表中的每个元素为协同租户的信息（包括租户 ID 与租户名称）。每个协同租户包含以下参数：

| 参数名称 | 参数类型   | 描述    |
|------|--------|-------|
| id   | string | 租户 ID |
| name | string | 租户名称  |

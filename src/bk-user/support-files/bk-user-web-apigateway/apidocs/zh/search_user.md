### 描述

搜索用户（包含协同用户），搜索结果默认返回前 100 条数据（如需更多搜索结果，需要细化搜索条件）

### 输入参数

| 参数名称                    | 参数类型   | 必选 | 描述                                                                      |
|-------------------------|--------|----|-------------------------------------------------------------------------|
| keyword                 | string | 是  | 搜索关键字（可输入 login_name（企业内用户唯一标识）或者 full_name（姓名）的值），至少输入长度为 1，至多输入长度为 64 |
| owner_tenant_id         | string | 否  | 数据源所属租户 ID，可指定租户 ID 搜索对应租户用户，默认为空（搜索本租户用户与协同租户用户）                       |
| with_organization_paths | bool   | 否  | 是否返回用户所属组织路径，默认为 false                                                  |

### 请求示例

```
// URL Query 参数
keyword=zhang&with_organization_paths=true
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "hc6n2ydjxtxef4cw",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "owner_tenant_id": "default",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AA"],
            "organizations": [
                [{"id": 1, "name": "公司"}, {"id": 2, "name": "部门A"}, {"id": 4, "name": "中心AA"}],
            ],
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "full_name": "张四",
            "display_name": "zhangsi(张四)",
            "owner_tenant_id": "collaborative_tenant",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AB", "公司/部门B/中心BA"],
            "organizations": [
                [{"id": 1, "name": "公司"}, {"id": 2, "name": "部门A"}, {"id": 5, "name": "中心AB"}],
                [{"id": 1, "name": "公司"}, {"id": 3, "name": "部门B"}, {"id": 6, "name": "中心BA"}],
            ],
        },
    ]
}
```

### 响应参数说明

| 参数名称               | 参数类型   | 描述                                                                      |
|--------------------|--------|-------------------------------------------------------------------------|
| bk_username        | string | 蓝鲸用户唯一标识                                                                |
| login_name         | string | 企业内用户唯一标识                                                               |
| full_name          | string | 用户姓名                                                                    |
| display_name       | string | 用户展示名                                                                   |
| owner_tenant_id    | string | 数据源所属租户 ID，本租户用户返回为本租户 ID，协同用户返回为其原始租户 ID                               |
| status             | string | 用户状态，其中 `enabled` 表示**启用**状态；`disabled` 表示**禁用**状态；`expired` 表示**过期**状态 |
| organization_paths | array  | 用户所属组织路径，多个以逗号分隔，格式为`部门1/部门2/.../部门n`                                   |
| organizations      | array  | 用户所属组织链列表，每个直属部门一条链（从根部门到直属部门，含直属部门自身），与 `organization_paths` 按下标一一对应，不受 `with_organization_paths` 影响 |
| organizations[][].id   | int    | 部门唯一标识，当前租户未同步该部门时为 `null`                                     |
| organizations[][].name | string | 部门名称                                                                    |

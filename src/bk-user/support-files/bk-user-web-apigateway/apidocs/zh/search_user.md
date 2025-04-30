### 描述

搜索用户（包含协同用户与虚拟用户），搜索结果默认返回前 100 条数据（如需更多搜索结果，需要细化搜索条件）

### 输入参数

| 参数名称                    | 参数类型   | 必选 | 描述                                                                      |
|-------------------------|--------|----|-------------------------------------------------------------------------|
| keyword                 | string | 是  | 搜索关键字（可输入 login_name（企业内用户唯一标识）或者 full_name（姓名）的值），至少输入长度为 1，至多输入长度为 64 |
| data_source_type        | string | 否  | 数据源类型，可选值为`real`（对应实名用户）、`virtual`（对应虚拟用户），默认为空（搜索实名 & 虚拟用户）            |
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
            "data_source_type": "real",
            "owner_tenant_id": "default",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AA"],
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "full_name": "张四",
            "display_name": "zhangsi(张四)",
            "data_source_type": "real",
            "owner_tenant_id": "collaborative_tenant",
            "status": "enabled",
            "organization_paths": ["公司/部门A/中心AB", "公司/部门B/中心BA"],
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangwu",
            "full_name": "张五",
            "display_name": "zhangwu(张五)",
            "data_source_type": "virtual",
            "owner_tenant_id": "default",
            "status": "disabled",
            "organization_paths": [],
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
| data_source_type   | string | 数据源类型, 其中 `real` 对应实名数据源（用户），`virtual` 对应虚拟数据源（用户）                      |
| owner_tenant_id    | string | 数据源所属租户 ID，本租户用户（包含虚拟用户）返回为本租户 ID, 协同用户返回为其原始租户 ID                      |
| status             | string | 用户状态，其中 `enabled` 表示**启用**状态；`disabled` 表示**禁用**状态；`expired` 表示**过期**状态 |
| organization_paths | array  | 用户所属组织路径，多个以逗号分隔，格式为`部门1/部门2/.../部门n`；虚拟用户无所属组织路径                       |

### 描述

搜索部门（包含协同部门），搜索结果默认返回前 100 条数据（如需更多搜索结果，需要细化搜索条件）

### 输入参数

| 参数名称            | 参数类型   | 必选 | 描述                                                |
|-----------------|--------|----|---------------------------------------------------|
| keyword         | string | 是  | 搜索关键字（部门名称），至少输入长度为 1，至多输入长度为 64                  |
| owner_tenant_id | string | 否  | 数据源所属租户 ID，可指定租户 ID 搜索对应租户部门，默认为空（搜索本租户部门与协同租户部门） |

### 请求示例

```
// URL Query 参数
keyword=中心A
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "owner_tenant_id": "default",
            "organization_path": "公司/部门A",
            "has_child": false,
            "has_user": true
        },
        {
            "id": 5,
            "name": "中心AB",
            "owner_tenant_id": "collaborative_tenant",
            "organization_path": "公司/部门A",
            "has_child": false,
            "has_user": false
        }
    ]
}
```

### 响应参数说明

| 参数名称              | 参数类型   | 描述                                         |
|-------------------|--------|--------------------------------------------|
| id                | int    | 部门唯一标识                                     |
| name              | string | 部门名称                                       |
| owner_tenant_id   | string | 数据源所属租户 ID，本租户部门返回为本租户 ID, 协同部门返回为其原始租户 ID |
| organization_path | string | 部门组织路径，格式为：`部门1/部门2/.../部门n`               |
| has_child         | bool   | 是否有子部门                                     |
| has_user          | bool   | 是否有所属用户                                    |

### 描述

批量查询用户（包含协同用户与虚拟用户）

### 输入参数

| 参数名称             | 参数类型   | 必选 | 描述                                                                             |
|------------------|--------|----|--------------------------------------------------------------------------------|
| lookups          | string | 是  | 精确匹配的值（可以为 bk_username、login_name 或 full_name），多个以逗号分隔，限制数量为 100，每个值最大输入长度为 64 |
| lookup_fields    | string | 是  | 匹配字段，多个以逗号分隔，每个元素可选值为`bk_username`、`login_name`、`full_name`                    |
| data_source_type | string | 否  | 数据源类型，可选值为`real`（对应实名用户）、`virtual`（对应虚拟用户），默认为空（查询实名 & 虚拟用户）                   |
| owner_tenant_id  | string | 否  | 数据源所属租户 ID，可指定租户 ID 查询对应租户用户，默认为空（查询本租户用户与协同租户用户）                              |

### 请求示例

```
// URL Query 参数
lookups=zhangsan,lisi&lookup_fields=login_name,bk_username
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
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "lisi",
            "full_name": "李四",
            "display_name": "lisi(李四)",
            "data_source_type": "real",
            "owner_tenant_id": "collaborative_tenant",
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangsan",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "data_source_type": "virtual",
            "owner_tenant_id": "default",
        },
    ]
}
```

### 响应参数说明

| 参数名称             | 参数类型   | 描述                                                 |
|------------------|--------|----------------------------------------------------|
| bk_username      | string | 蓝鲸用户唯一标识                                           |
| login_name       | string | 企业内用户唯一标识                                          |
| full_name        | string | 用户姓名                                               |
| display_name     | string | 用户展示名                                              |
| data_source_type | string | 数据源类型, 其中 `real` 对应实名数据源（用户），`virtual` 对应虚拟数据源（用户） |
| owner_tenant_id  | string | 数据源所属租户 ID，本租户用户（包含虚拟用户）返回为本租户 ID, 协同用户返回为其原始租户 ID |

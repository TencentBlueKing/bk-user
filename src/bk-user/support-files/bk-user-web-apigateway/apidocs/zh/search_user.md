### 描述

搜索用户（包含协同用户与虚拟用户），搜索结果默认返回前 100 条数据（如需更多搜索结果，需要细化搜索条件）

### 输入参数

| 参数名称    | 参数类型   | 必选 | 描述                                                 |
|---------|--------|----|----------------------------------------------------|
| keyword | string | 否  | 搜索关键字（可输入 login_name（企业内用户唯一标识）或者 full_name（姓名）的值） |

### 请求示例

```
// URL Query 参数
keyword=张
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "bk_username": "hc6n2ydjxtxef4cw",
            "login_name": "zhangsan",
            "display_name": "张三",
            "type": "real",
            "tenant_id": "",
            "tenant_name": ""
        },
        {
            "bk_username": "frywzyv2n0bilwgb",
            "login_name": "zhangsi",
            "display_name": "张四",
            "type": "real",
            "tenant_id": "test",
            "tenant_name": "测试协同租户"
        },
        {
            "bk_username": "uvatls6netj2jmck",
            "login_name": "zhangwu",
            "display_name": "张五",
            "type": "virtual",
            "tenant_id": "",
            "tenant_name": ""
        },
    ]
}
```

### 响应参数说明

| 参数名称         | 参数类型   | 描述                                        |
|--------------|--------|-------------------------------------------|
| bk_username  | string | 蓝鲸用户唯一标识                                  |
| login_name   | string | 企业内用户唯一标识                                 |
| display_name | string | 用户展示名                                     |
| type         | string | 用户类型, 其中 `real` 表示实名用户，`virtual` 表示虚拟用户   |
| tenant_id    | string | 租户 ID，本租户用户（包含虚拟用户）返回为"", 协同用户返回为其原始租户 ID |
| tenant_name  | string | 租户名称，本租户用户（包含虚拟用户）返回为"", 协同租户返回为其原始租户名称   |

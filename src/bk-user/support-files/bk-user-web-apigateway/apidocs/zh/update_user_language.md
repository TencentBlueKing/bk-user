### 描述

更新用户语言信息

### 输入参数

| 参数名称        | 参数类型   | 必选 | 参数位置 | 描述                         |
|-------------|--------|----|------|----------------------------|
| bk_username | string | 是  | path | 蓝鲸用户唯一标识                   |
| language    | string | 是  | body | 语言类型（中文为 `zh-cn`，英文为 `en`） |

### 请求示例

```
// URL Path 参数
/api/v3/open-web/tenant/users/7idwx3b7nzk6xigs/language/
```

```json5
// 请求体
{
    "language": "zh-cn"
}
```

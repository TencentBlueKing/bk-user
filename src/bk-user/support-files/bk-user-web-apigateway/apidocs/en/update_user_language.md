### Description

Update user's language information

### Parameters

| Name        | Type   | Required | Location | Description                                     |
|-------------|--------|----------|----------|-------------------------------------------------|
| bk_username | string | Yes      | path     | Blueking user's unique identifier               |
| language    | string | Yes      | body     | Language type (Chinese: 'zh-cn', English: 'en') |

### Request Example

```
// URL Path 参数
/api/v3/open-web/tenant/users/7idwx3b7nzk6xigs/language/
```

```json5
// Request Body
{
    "language": "zh-cn"
}
```

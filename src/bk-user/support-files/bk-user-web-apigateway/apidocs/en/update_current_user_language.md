### Description

Update current user's language information

### Parameters

| Name        | Type   | Required | Description                                     |
|-------------|--------|----------|-------------------------------------------------|
| language    | string | Yes      | Language type (Chinese: 'zh-cn', English: 'en') |

### Request Example

```json5
// Request Body
{
    "language": "zh-cn"
}
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "language": "zh-cn"
    }
}
```

### Response Parameters Description

| Name     | Type   | Description                                     |
|----------|--------|-------------------------------------------------|
| language | string | Language type (Chinese: 'zh-cn', English: 'en') |

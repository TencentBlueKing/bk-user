### Description

(Pagination) Query user's list

### Parameters

| Name      | Type | Required | Description                                 |
|-----------|------|----------|---------------------------------------------|
| page      | int  | No       | Page number, default is 1                   |
| page_size | int  | No       | The number of pages per page, default is 10 |

### Request Example

```
// URL Query Parameters
page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
  "data": {
    "count": 2,
    "results": [
      {
        "tenant_id": "default",
        "bk_username": "q9k6bhqks0ckl5ew",
        "display_name": "张三",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
      },
      {
        "tenant_id": "default",
        "bk_username": "er0ugcammqwf1q5w",
        "display_name": "李四",
        "time_zone": "Asia/Shanghai",
        "language": "zh-cn",
      }
    ],
  }
}
```

### Response Parameters Description

| Name         | Type   | Description                       |
|--------------|--------|-----------------------------------|
| tenant_id    | string | Tenant ID                         |
| bk_username  | string | Blueking user's unique identifier |
| display_name | string | User's display_name               |
| time_zone    | string | Time Zone                         |
| language     | string | Language                          |

# Response Example for Non-200 Status Code

No response example

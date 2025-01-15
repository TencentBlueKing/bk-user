### Description

(Pagination) Query user's list

### Parameters

| Name          | Type   | Required | Description                                                         |
|---------------|--------|----------|---------------------------------------------------------------------|
| lookup_field  | string | No       | Query field name (supports bk_username, display_name, email, phone) |
| exact_lookups | string | No       | Exact query field value list, separated by commas                   |
| fuzzy_lookups | string | No       | Fuzzy query field value list, separated by commas                   |
| page          | int    | No       | Page number, default is 1                                           |
| page_size     | int    | No       | The number of pages per page, default is 10                         |

***Note***: If both exact_lookups and fuzzy_lookups fields are provided, only the exact_lookups field will be used for
the query.

### Request Example

```
// URL Query Parameters
lookup_field=bk_username&exact_lookups=q9k6bhqks0ckl5ew,er0ugcammqwf1q5w
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

The returned user list is sorted in ascending order by bk_username according to the query conditions. If there is no
query condition, all user lists are returned.

# Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Arguments Validation Failed: lookup_field:  xxx is not a valid choice.",
  }
}
```

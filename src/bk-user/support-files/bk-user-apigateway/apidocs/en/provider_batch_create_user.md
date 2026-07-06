### Description

Batch create users (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name                       | Type   | Required | Description                     |
|----------------------------|--------|----------|---------------------------------|
| users                      | array  | Yes      | User list, max 100 items        |
| users[].id                 | string | Yes      | User unique ID (within data source) |
| users[].username           | string | Yes      | Username                        |
| users[].full_name          | string | Yes      | Full name                       |
| users[].email              | string | No       | Email                           |
| users[].phone              | string | No       | Phone number                    |
| users[].phone_country_code | string | No       | Phone country code, default 86  |
| users[].extras             | object | No       | Custom fields                   |

### Request Example

```json
{
    "users": [
        {
            "id": "emp_001",
            "username": "zhangsan",
            "full_name": "Zhang San",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "phone_country_code": "86",
            "extras": {}
        }
    ]
}
```

### Response Example

```
HTTP 201 Created
```

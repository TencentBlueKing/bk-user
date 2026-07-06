### Description

Batch update users (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name                       | Type   | Required | Description                          |
|----------------------------|--------|----------|--------------------------------------|
| users                      | array  | Yes      | User list, max 100 items             |
| users[].id                 | string | Yes      | User unique ID (within data source)  |
| users[].username           | string | No       | Username                             |
| users[].full_name          | string | No       | Full name                            |
| users[].email              | string | No       | Email                                |
| users[].phone              | string | No       | Phone number                         |
| users[].phone_country_code | string | No       | Phone country code                   |
| users[].extras             | object | No       | Custom fields                        |

### Request Example

```json
{
    "users": [
        {
            "id": "emp_001",
            "full_name": "Zhang San (Updated)",
            "email": "new@example.com"
        }
    ]
}
```

### Response Example

```
HTTP 204 No Content
```

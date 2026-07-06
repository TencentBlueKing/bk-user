### Description

Batch delete user-department relations (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name                        | Type   | Required | Description                               |
|-----------------------------|--------|----------|-------------------------------------------|
| relations                   | array  | Yes      | Relation list, max 100                    |
| relations[].user_id         | string | Yes      | User unique ID (within data source)       |
| relations[].department_id   | string | Yes      | Department unique ID (within data source) |

### Request Example

```json
{
    "relations": [
        {"user_id": "emp_001", "department_id": "dept_a"}
    ]
}
```

### Response Example

```
HTTP 204 No Content
```

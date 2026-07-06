### Description

Batch update departments (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name               | Type   | Required | Description                               |
|--------------------|--------|----------|-------------------------------------------|
| departments        | array  | Yes      | Department list, max 100 items            |
| departments[].id   | string | Yes      | Department unique ID (within data source) |
| departments[].name | string | Yes      | Department name                           |

### Request Example

```json
{
    "departments": [
        {"id": "dept_a", "name": "Engineering Center"}
    ]
}
```

### Response Example

```
HTTP 204 No Content
```

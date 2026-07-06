### Description

Batch create departments (Data Provider exclusive API)

Note: Departments are created as root departments by default. Parent-child relationships should be set via the `department-relations` API separately.

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name                 | Type   | Required | Description                               |
|----------------------|--------|----------|-------------------------------------------|
| departments          | array  | Yes      | Department list, max 100 items            |
| departments[].id     | string | Yes      | Department unique ID (within data source) |
| departments[].name   | string | Yes      | Department name                           |

### Request Example

```json
{
    "departments": [
        {"id": "company", "name": "Head Office"},
        {"id": "dept_a", "name": "Department A"}
    ]
}
```

### Response Example

```
HTTP 201 Created
```

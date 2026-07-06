### Description

Batch delete departments (Data Provider exclusive API)

Note: Cannot delete departments that have sub-departments or associated users.

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name  | Type  | Required | Description                                |
|-------|-------|----------|--------------------------------------------|
| ids   | array | Yes      | Department unique ID list, max 100 items   |

### Request Example

```json
{
    "ids": ["dept_a", "dept_b"]
}
```

### Response Example

```
HTTP 204 No Content
```

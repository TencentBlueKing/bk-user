### Description

Batch delete users (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name  | Type  | Required | Description                             |
|-------|-------|----------|-----------------------------------------|
| ids   | array | Yes      | User unique ID list, max 100 items      |

### Request Example

```json
{
    "ids": ["emp_001", "emp_002"]
}
```

### Response Example

```
HTTP 204 No Content
```

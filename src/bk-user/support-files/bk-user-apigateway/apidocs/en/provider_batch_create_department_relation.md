### Description

Batch create department parent-child relations (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name               | Type   | Required | Description                                        |
|--------------------|--------|----------|----------------------------------------------------|
| relations          | array  | Yes      | Relation list, max 100 items                       |
| relations[].id     | string | Yes      | Department unique ID (within data source)          |
| relations[].parent | string | Yes      | Parent department ID, null means set as root       |

### Request Example

```json
{
    "relations": [
        {"id": "dept_a", "parent": "company"},
        {"id": "dept_b", "parent": null}
    ]
}
```

### Response Example

```
HTTP 204 No Content
```

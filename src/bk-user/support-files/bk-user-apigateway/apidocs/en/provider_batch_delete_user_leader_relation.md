### Description

Batch delete user-leader relations (Data Provider exclusive API)

### Path Parameters

| Name           | Type | Required | Description    |
|----------------|------|----------|----------------|
| data_source_id | int  | Yes      | Data source ID |

### Request Parameters

| Name                      | Type   | Required | Description                          |
|---------------------------|--------|----------|--------------------------------------|
| relations                 | array  | Yes      | Relation list, max 100 items         |
| relations[].user_id       | string | Yes      | User unique ID (within data source)  |
| relations[].leader_ids    | array  | Yes      | Leader user unique IDs to delete     |

### Request Example

```json
{
    "relations": [
        {
            "user_id": "emp_001",
            "leader_ids": ["emp_100"]
        }
    ]
}
```

### Response Example

```
HTTP 204 No Content
```

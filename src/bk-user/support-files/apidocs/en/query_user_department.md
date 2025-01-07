### Description

Query user's information of department

### Parameters

| Name           | Type    | Required | Description                                    |
|----------------|---------|----------|------------------------------------------------|
| bk_username    | string  | Yes      | Blueking user's unique identifier              |
| with_ancestors | boolean | No       | Whether to include ancestors, default is false |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/users/mzmwjffhhbjg4fxz/departments/?with_ancestors=true
```

### Response Example for Status Code 200

```json5
{
  "data": [
    {
      "id": 3,
      "name": "部门C",
      "ancestors": [
        {
          "id": 1,
          "name": "部门A"
        },
        {
          "id": 2,
          "name": "部门B"
        }
      ]
    },
    {
      "id": 6,
      "name": "部门F",
      "ancestors": [
        {
          "id": 1,
          "name": "部门A"
        },
        {
          "id": 4,
          "name": "部门D"
        },
        {
          "id": 5,
          "name": "部门E"
        }
      ]
    }
  ]
}
```

### Response Parameters Description

| Name      | Type   | Description                  |
|-----------|--------|------------------------------|
| id        | int    | Tenant department ID         |
| name      | string | Tenant department name       |
| ancestors | list   | List of ancestry departments |

#### Ancestors Parameters Description

Ancestors is a list of ancestral departments. Each element in the list is the ancestry department information of the
corresponding department, arranged in descending order (from root ancestry department -> direct ancestry department).
Each element contains the following parameters:

| Name | Type   | Description            |
|------|--------|------------------------|
| id   | int    | Tenant department ID   |
| name | string | Tenant department name |

# Response Example for Non-200 Status Code

```json5
// status_code = 400
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Cannot find the corresponding tenant user"
  }
}
```

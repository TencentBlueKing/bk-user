### Description

Query virtual user's information of bk_username

### Parameters

| Name       | Type   | Required | Location    | Description                                    |
|------------|--------|----------|-------------|------------------------------------------------|
| login_name | string | Yes      | path        | Unique identifier of the department            |

### Request Example

```
// URL Path Parameter
/api/v3/open/tenant/virtual-users/{login_name}/bk_username/
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "bk_username": "7idwx3b7nzk6xigs"
    }
}
```

### Response Parameters Description

| Name         | Type   | Description                       |
|--------------|--------|-----------------------------------|
| bk_username  | string | Blueking user's unique identifier |

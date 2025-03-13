### Description

(Pagination) Query the sub-department list based on the department ID, support recursive query by level

### Parameters

| Name          | Type | Required | Location    | Description                                                                                                         |
|---------------|------|----------|-------------|---------------------------------------------------------------------------------------------------------------------|
| page          | int  | No       | query param | Page number, default is 1                                                                                           |
| page_size     | int  | No       | query param | The number of pages per page, default is 10, maximum is 500                                                         |
| department_id | int  | Yes      | path        | Unique identifier of the department                                                                                 |
| max_level     | int  | No       | query param | The maximum relative level of the recursive sub-department. The default is 1, which means the direct sub-department |

### Request Example

```
// URL Path & Query Parameters
/api/v3/open/tenant/departments/2/descendants/?max_level=2&page=1&page_size=5
```

### Response Example for Status Code 200

```json5
{
    "data": {
        "count": 4,
        "results": [
            {
                "id": 4,
                "name": "中心AA",
                "parent_id": 2
            },
            {
                "id": 5,
                "name": "中心AB",
                "parent_id": 2
            },
            {
                "id": 6,
                "name": "小组AAA",
                "parent_id": 4
            },
            {
                "id": 7,
                "name": "小组ABA",
                "parent_id": 5
            }
        ]
    }
}
```

### Response Parameters Description

| Name      | Type   | Description                         |
|-----------|--------|-------------------------------------|
| id        | int    | Unique identifier of the department |
| name      | string | The name of the department          |
| parent_id | int    | The parent department ID            |

For example, if the sub-departments of Department A are Center AA and Center AB, the sub-department of Center AA is
Group AAA, and the sub-department of Center AB is Group ABA, then the sub-department of Department A with a relative
level of level 2 is: Center AA -> Center AB -> Group AAA -> Group ABA

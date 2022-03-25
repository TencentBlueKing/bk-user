### 描述

获取部门内的人员

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| detail | `query` | boolean |  | 是否返回全部字段 |
| fields | `query` | string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 指定查询字段，内容为 lookup_value 所属字段, 例如: username |
| ordering | `query` | string |  | Which field to use when ordering the results. |
| page | `query` | integer |  | A page number within the paginated result set. |
| page_size | `query` | integer |  | Number of results to return per page. |
| recursive | `query` | boolean |  | 是否递归 |
| wildcard_search | `query` | string |  | 模糊查找用户的 username & display_name 字段 |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

V2DepartmentsProfilesReadOKBody

##### 内联模型

**V2DepartmentsProfilesReadOKBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| count | integer| 是 |  |  |
| next | uri (formatted string)|  |  |  |
| previous | uri (formatted string)|  |  |  |
| results | []V2DepartmentsProfilesReadOKBodyResultsItems0| 是 |  |  |



**V2DepartmentsProfilesReadOKBodyResultsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| category_id | integer|  |  |  |
| code | string|  |  |  |
| enabled | boolean|  |  |  |
| extras | interface{}|  |  |  |
| full_name | string|  |  |  |
| has_children | boolean|  |  |  |
| id | integer|  |  |  |
| level | integer|  |  |  |
| lft | integer|  |  |  |
| name | string| 是 |  |  |
| order | integer|  |  |  |
| parent | integer|  |  |  |
| rght | integer|  |  |  |
| tree_id | integer|  |  |  |
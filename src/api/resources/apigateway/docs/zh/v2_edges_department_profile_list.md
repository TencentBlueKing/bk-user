### 描述

获取对象列表

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| best_match | `query` | boolean |  | 是否按照最短匹配排序 |
| exact_lookups | `query` | []string |  | 精确查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish |
| fields | `query` | []string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| fuzzy_lookups | `query` | []string |  | 模糊查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 查询字段，针对 exact_lookups,fuzzy_lookups 生效 |
| ordering | `query` | string |  | Which field to use when ordering the results. |
| page | `query` | integer |  | A page number within the paginated result set. |
| page_size | `query` | integer |  | Number of results to return per page. |
| since | `query` | date-time (formatted string) |  | 筛选某个时间点后的记录 |
| time_field | `query` | string |  | 时间过滤字段，支持 update_time, create_time |
| until | `query` | date-time (formatted string) |  | 筛选某个时间点前的记录 |
| wildcard_search | `query` | string |  | 在多个字段模糊搜索的内容 |
| wildcard_search_fields | `query` | []string |  | 指定多个模糊搜索字段 |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

V2EdgesDepartmentProfileListOKBody

##### 内联模型

**V2EdgesDepartmentProfileListOKBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| count | integer| 是 |  |  |
| next | uri (formatted string)|  |  |  |
| previous | uri (formatted string)|  |  |  |
| results | []V2EdgesDepartmentProfileListOKBodyResultsItems0| 是 |  |  |



**V2EdgesDepartmentProfileListOKBodyResultsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| department_id | integer|  |  |  |
| id | integer|  |  |  |
| profile_id | integer|  |  |  |
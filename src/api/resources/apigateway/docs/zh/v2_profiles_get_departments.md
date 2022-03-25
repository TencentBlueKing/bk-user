### 描述

获取用户所属部门信息

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| fields | `query` | string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 指定查询字段，内容为 lookup_value 所属字段, 例如: username |
| ordering | `query` | string |  | Which field to use when ordering the results. |
| page | `query` | integer |  | A page number within the paginated result set. |
| page_size | `query` | integer |  | Number of results to return per page. |
| with_ancestors | `query` | boolean |  | 是否返回所有祖先 |
| with_family | `query` | boolean |  | 是否返回所有祖先（兼容） |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

[]V2ProfilesGetDepartmentsOKBodyItems0

##### 内联模型

**V2ProfilesGetDepartmentsOKBodyItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| full_name | string|  |  |  |
| id | integer|  |  |  |
| name | string| 是 |  |  |
| order | integer|  |  |  |
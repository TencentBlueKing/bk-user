### 描述

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| fields | `query` | string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 指定查询字段，内容为 lookup_value 所属字段, 例如: username |
| with_ancestors | `query` | boolean |  |  |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

V2DepartmentsReadOKBody

##### 内联模型

**V2DepartmentsReadOKBody**



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
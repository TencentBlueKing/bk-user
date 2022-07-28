### 描述

获取详细信息

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| fields | `query` | string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 指定查询字段，内容为 lookup_value 所属字段, 例如: username |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

V2ProfilesReadOKBody

##### 内联模型

**V2ProfilesReadOKBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| category_id | integer| 是 |  |  |
| code | string|  |  |  |
| country_code | string|  |  |  |
| create_time | date-time (formatted string)|  |  |  |
| departments | []V2ProfilesReadOKBodyDepartmentsItems0|  |  |  |
| display_name | string|  |  |  |
| domain | string|  |  |  |
| email | email (formatted string)|  |  |  |
| enabled | boolean|  |  |  |
| extras | interface{}|  |  |  |
| id | integer|  |  |  |
| iso_code | string|  |  |  |
| language | string|  |  |  |
| last_login_time | date-time (formatted string)|  |  |  |
| leader | []V2ProfilesReadOKBodyLeaderItems0|  |  |  |
| logo | string|  |  |  |
| password_update_time | date-time (formatted string)|  |  |  |
| password_valid_days | integer|  |  |  |
| position | integer|  |  |  |
| qq | string|  |  |  |
| role | integer|  |  |  |
| staff_status | string|  |  |  |
| status | string|  |  |  |
| telephone | string|  |  |  |
| time_zone | string|  |  |  |
| type | string|  |  |  |
| update_time | date-time (formatted string)|  |  |  |
| username | string|  |  |  |
| wx_openid | string|  |  |  |
| wx_userid | string|  |  |  |



**V2ProfilesReadOKBodyDepartmentsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| full_name | string|  |  |  |
| id | integer|  |  |  |
| name | string| 是 |  |  |
| order | integer|  |  |  |



**V2ProfilesReadOKBodyLeaderItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| display_name | string|  |  |  |
| id | integer|  |  |  |
| username | string|  |  |  |
### 描述

登录信息校验

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| data | `body` | V1LoginLoginBody | 是 |  |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

#### 200
Status: OK

##### Schema

V1LoginLoginOKBody

##### 内联模型

**V1LoginLoginBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| domain | string|  | 用户所属目录 domain，当登录用户不属于默认目录时必填 |  |
| password | string| 是 | 用户密码 |  |
| username | string| 是 | 用户名 |  |



**V1LoginLoginOKBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| category_id | integer| 是 |  |  |
| code | string|  |  |  |
| country_code | string|  |  |  |
| create_time | date-time (formatted string)|  |  |  |
| departments | []V1LoginLoginOKBodyDepartmentsItems0|  |  |  |
| display_name | string|  |  |  |
| domain | string|  |  |  |
| email | email (formatted string)|  |  |  |
| enabled | boolean|  |  |  |
| extras | interface{}|  |  |  |
| id | integer|  |  |  |
| iso_code | string|  |  |  |
| language | string|  |  |  |
| last_login_time | date-time (formatted string)|  |  |  |
| leader | []V1LoginLoginOKBodyLeaderItems0|  |  |  |
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



**V1LoginLoginOKBodyDepartmentsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| full_name | string|  |  |  |
| id | integer|  |  |  |
| name | string| 是 |  |  |
| order | integer|  |  |  |



**V1LoginLoginOKBodyLeaderItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| display_name | string|  |  |  |
| id | integer|  |  |  |
| username | string|  |  |  |
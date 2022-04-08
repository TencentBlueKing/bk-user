### 描述

登陆均为兼容代码

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| data | `body` | V1LoginUpsertBody | 是 |  |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 201 | Created |  |

### 响应

#### 201
Status: Created

##### Schema

V1LoginUpsertCreatedBody

##### 内联模型

**V1LoginUpsertBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| display_name | string|  |  |  |
| domain | string|  |  |  |
| email | email (formatted string)|  |  |  |
| language | string|  |  |  |
| position | string|  |  |  |
| qq | string|  |  |  |
| role | integer|  |  |  |
| staff_status | string|  |  |  |
| status | string|  |  |  |
| telephone | string|  |  |  |
| time_zone | string|  |  |  |
| username | string| 是 |  |  |
| wx_userid | string|  |  |  |



**V1LoginUpsertCreatedBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| display_name | string|  |  |  |
| domain | string|  |  |  |
| email | email (formatted string)|  |  |  |
| language | string|  |  |  |
| position | string|  |  |  |
| qq | string|  |  |  |
| role | integer|  |  |  |
| staff_status | string|  |  |  |
| status | string|  |  |  |
| telephone | string|  |  |  |
| time_zone | string|  |  |  |
| username | string| 是 |  |  |
| wx_userid | string|  |  |  |
### 描述

登陆均为兼容代码

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| data | `body` | V1LoginProfileBatchQueryBody | 是 |  |

### 所有响应
| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 201 | Created |  |

### 响应

#### 201
Status: Created

##### Schema

V1LoginProfileBatchQueryCreatedBody

##### 内联模型

**V1LoginProfileBatchQueryBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| is_complete | boolean|  |  |  |
| username_list | []string|  |  |  |



**V1LoginProfileBatchQueryCreatedBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| is_complete | boolean|  |  |  |
| username_list | []string|  |  |  |
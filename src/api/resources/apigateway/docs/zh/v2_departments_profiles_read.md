### 描述

获取部门内的人员

返回结果以用户主键为单位去重，`count` 为满足当前部门范围和查询条件的唯一用户数。
`recursive=true` 包含当前部门及其后代部门；同一用户属于多个命中部门时只出现一次。

`no_page=true` 仅兼容受控结果集，默认最多 10000 名用户。超过上限会返回参数错误，要求从
`page=1` 开始使用 `page/page_size`，不会静默截断。上限只由 `USER_LIST_NO_PAGE_LIMIT` 控制。
限额内响应保持顶层数组，关系字段使用与分页用户对象一致的数组结构。
分页请求的每页数量由 `MAX_PAGE_SIZE` 控制；请求值超过配置上限时沿用旧行为自动收敛到上限。

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| detail | `query` | boolean |  | 保留参数，当前成员响应不据此切换字段集合。 |
| fields | `query` | string |  | 保留参数，当前成员响应固定使用用户响应序列化器，不据此裁剪成员字段；不能照搬用户列表接口的字段选择能力。 |
| include_disabled | `query` | boolean |  | 不用于切换成员用户的停用筛选。非递归查询排除状态为 DELETED 的成员；递归查询仅返回 enabled=true 的成员。 |
| lookup_field | `query` | string |  | 解释路径中 lookup_value 的部门字段，默认 id，例如按部门 code 查找；不是成员用户的筛选字段。 |
| ordering | `query` | string |  | 不控制返回成员的排序。非递归成员按用户 ID 升序，递归成员按用户 ID 降序；不能通过此参数切换成员排序。 |
| page | `query` | integer |  | 页码，从 1 开始，默认 1；`no_page=true` 时不使用。 |
| page_size | `query` | integer |  | 每页条数，默认 50；上限由服务端 MAX_PAGE_SIZE 配置，默认 10000，超过上限时取上限；`no_page=true` 时不使用。 |
| no_page | `query` | boolean |  | 默认 false。true 表示不分页；受 USER_LIST_NO_PAGE_LIMIT 限制，默认最多返回 10000 名唯一用户，超限报错而非截断。 |
| recursive | `query` | boolean |  | 默认 false，仅查询当前部门成员；true 包含当前部门及其后代部门成员。 |
| wildcard_search | `query` | string |  | 模糊查找用户的 username & display_name 字段 |

### 分页方式与兼容性

- 成员范围由路径指定的部门、`recursive` 和 `wildcard_search` 决定。
  当前接口不提供用户列表接口的 `exact_lookups/fuzzy_lookups` 成员筛选方式。
- 两段查询由服务端配置决定，默认关闭；开启后，实际
  `OFFSET=(page-1)×实际 page_size` 达到 `DEFERRED_PAGINATION_MIN_OFFSET`（默认 20000），
  且查询结构满足安全条件时，采用“先查本页 ID，再按实际 ID 查询资料”，保留原成员范围和排序。
  不满足条件时继续普通分页。两段不消除 COUNT、关系加载和响应组装成本。
- `no_page` 限额内仍返回数组，但成员对象统一采用与分页一致的序列化规则，部门、上级关系作为嵌套数组，
  不再按关系平铺成多行；自定义字段和字段格式也按序列化规则处理。依赖旧平铺结构的调用方需要调整。
- 超过 `no_page` 上限的调用需去掉该参数，从第一页开始分页读取。
  关闭两段查询开关不会解除此上限，也不会恢复旧平铺结构。

### 所有响应

| 状态码 | 状态 | 描述 |
|------|--------|-------------|
| 200 | OK |  |

### 响应

以下为业务数据结构：普通分页返回 `{"count": 唯一用户总数, "results": [用户对象]}`，
不返回 `next`、`previous`；`no_page=true` 成功时返回 `[用户对象]`，无 `count/results` 包装。
启用企业统一响应封装时，业务数据位于 `data` 中；错误应检查 `result`、`code` 和 `message`，
不能仅凭 HTTP 200 判断成功。原始响应模式下参数错误使用 HTTP 4xx。

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
| results | []V2DepartmentsProfilesReadOKBodyResultsItems0| 是 |  |  |



**V2DepartmentsProfilesReadOKBodyResultsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| id | integer | 是 | 用户 ID | |
| username | string | 是 | 用户名 | |
| display_name | string | | 显示名称 | |
| category_id | integer | | 用户目录 ID | |
| domain | string | | 用户域 | |
| enabled | boolean | | 是否启用 | |
| status | string | | 用户状态 | |
| staff_status | string | | 在职状态 | |
| email | string | | 邮箱 | |
| telephone | string | | 电话 | |
| qq | string | | QQ | |
| wx_userid | string | | 企业微信用户 ID | |
| logo | string | | 头像 | |
| password_valid_days | integer | | 密码有效期 | |
| account_expiration_date | string | | 账号过期时间 | |
| create_time | date-time | | 创建时间 | |
| update_time | date-time | | 更新时间 | |
| country_code | string | | 国家区号 | |
| iso_code | string | | 国家代码 | |
| language | string | | 语言 | |
| time_zone | string | | 时区 | |
| position | integer | | 职位 | |
| extras | object | | 按序列化规则处理的自定义字段 | |
| last_login_time | null | | 当前接口固定返回 null | |
| departments | []object | | 所属部门；对象包含 id、name、full_name、order | |
| leader | []object | | 上级；对象包含 id、username、display_name | |

返回主体是用户，不是部门节点；部门的 `lft/rght/tree_id` 不作为成员用户的顶层字段返回。
实际可见字段仍受敏感字段权限控制。

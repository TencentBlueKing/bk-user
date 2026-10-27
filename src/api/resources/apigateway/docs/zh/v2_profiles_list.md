### 描述

获取用户列表

返回结果以用户主键为单位去重，`count` 为满足条件的唯一用户数，去重在分页前完成。
按多个部门或上级条件查询时，同一用户只出现一次；`departments`、`leader` 在用户对象中作为数组返回。
支持接口允许的用户自身字段排序，例如 `id`、`display_name`；不支持
`ordering=departments`、`ordering=leader` 等多值关系排序，使用这些排序会返回参数错误。
未指定排序时通常按用户 ID 升序；启用最短匹配等搜索排序时，以最终查询排序为准。
非主键排序会补充用户主键作为同值时的排序依据，不改变原字段的排序优先级。

`no_page=true` 仅兼容受控结果集，默认最多 10000 名用户。超过上限会返回参数错误，要求从
`page=1` 开始使用 `page/page_size`，不会静默截断。上限只由 `USER_LIST_NO_PAGE_LIMIT` 控制。
限额内响应保持顶层数组，用户字段及关系结构与分页结果中的用户对象一致。
分页请求的每页数量由 `MAX_PAGE_SIZE` 控制；请求值超过配置上限时沿用旧行为自动收敛到上限。
不分页请求显式指定的 `fields` 必须是当前用户响应序列化器支持的字段；不支持的字段会明确报错，
不会静默丢弃。`for_sync` 请求仍采用同步专用字段定义。

### 输入参数

| 参数名称 | 参数位置 | 类型 | 必选 | 描述 |
|------|--------|------| :------: |-------------|
| best_match | `query` | boolean |  | 是否按照最短匹配排序 |
| exact_lookups | `query` | []string |  | 精确查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish |
| fields | `query` | []string |  | 指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id |
| fuzzy_lookups | `query` | []string |  | 模糊查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish |
| include_disabled | `query` | boolean |  | 是否包含已软删除的数据 |
| lookup_field | `query` | string |  | 查询字段，针对 exact_lookups,fuzzy_lookups 生效 |
| ordering | `query` | string |  | 排序字段；前缀 `-` 表示降序，多个字段用逗号分隔，例如 `-display_name,id`。支持接口允许的用户自身字段，不支持部门、上级等多值关系排序。其他合法非 ID 排序走普通分页，不因无法使用两段查询而报错。 |
| page | `query` | integer |  | 页码，从 1 开始，默认 1；`no_page=true` 时不使用。 |
| page_size | `query` | integer |  | 每页条数，默认 50；上限由服务端 `MAX_PAGE_SIZE` 配置，默认 10000，超过上限时取上限；`no_page=true` 时不使用。 |
| no_page | `query` | boolean |  | 默认 false。true 表示不分页；受 `USER_LIST_NO_PAGE_LIMIT` 限制，默认最多返回 10000 名唯一用户，超限报错而非截断。 |
| since | `query` | date-time (formatted string) |  | 筛选某个时间点后的记录 |
| time_field | `query` | string |  | 时间过滤字段，支持 update_time, create_time |
| until | `query` | date-time (formatted string) |  | 筛选某个时间点前的记录 |
| wildcard_search | `query` | string |  | 在多个字段模糊搜索的内容 |
| wildcard_search_fields | `query` | []string |  | 指定多个模糊搜索字段 |

### 分页方式与兼容性

- 两段查询由服务端配置决定，调用方不需要新增参数。默认关闭；开启后，实际
  `OFFSET=(page-1)×实际 page_size` 达到 `DEFERRED_PAGINATION_MIN_OFFSET`（默认 20000），
  且最终仅按 `id` 或 `-id` 排序、查询结构允许拆分时，采用“先查本页 ID，再按实际 ID 查询资料”。
  其他合法查询继续普通分页；两种方式均保留原筛选条件及唯一用户计数，不保证所有请求加速。
- 多部门等多值关联查询修复重复用户后，`count`、总页数和同页用户可能与旧版不同。
  升级后应从第一页重新开始分页，不沿用旧版的中途分页进度。
- 原有多值关系排序调用需改为支持的用户字段排序。
- `no_page` 限额内仍返回数组，但不再将部门、上级关系平铺成多行。
  用户对象采用与普通分页相同的序列化规则，可能包含嵌套关系数组、默认自定义字段及字段格式处理；
  依赖旧平铺结构的调用方需要调整。未请求的字段及敏感字段按原有字段选择、权限规则处理。
- 去重、关系排序校验和 `no_page` 限量不受两段开关控制；关闭两段不恢复旧版行为。

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

V2ProfilesListOKBody

##### 内联模型

**V2ProfilesListOKBody**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| count | integer| 是 |  |  |
| results | []V2ProfilesListOKBodyResultsItems0| 是 |  |  |



**V2ProfilesListOKBodyResultsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| account_expiration_date | string|  | 账号过期时间 |  |
| category_id | integer|  |  |  |
| country_code | string|  |  |  |
| create_time | date-time (formatted string)|  |  |  |
| departments | []V2ProfilesListOKBodyResultsItems0DepartmentsItems0|  |  |  |
| display_name | string|  |  |  |
| domain | string|  |  |  |
| email | string|  |  |  |
| enabled | boolean|  |  |  |
| extras | interface{}|  |  |  |
| id | integer|  |  |  |
| iso_code | string|  |  |  |
| language | string|  |  |  |
| last_login_time | null|  | 当前接口固定返回 null，不提供最近登录时间 |  |
| leader | []V2ProfilesListOKBodyResultsItems0LeaderItems0|  |  |  |
| logo | string|  |  |  |
| password_valid_days | integer|  |  |  |
| position | integer|  |  |  |
| qq | string|  |  |  |
| staff_status | string|  |  |  |
| status | string|  |  |  |
| telephone | string|  |  |  |
| time_zone | string|  |  |  |
| update_time | date-time (formatted string)|  |  |  |
| username | string| 是 |  |  |
| wx_userid | string|  |  |  |



**V2ProfilesListOKBodyResultsItems0DepartmentsItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| full_name | string|  |  |  |
| id | integer|  |  |  |
| name | string| 是 |  |  |
| order | integer|  |  |  |



**V2ProfilesListOKBodyResultsItems0LeaderItems0**



**Properties**

| 名称 | 类型 | 必选 | 描述 | 示例 |
|------|------|:--------:|-------------|---------|
| display_name | string|  |  |  |
| id | integer|  |  |  |
| username | string|  |  |  |

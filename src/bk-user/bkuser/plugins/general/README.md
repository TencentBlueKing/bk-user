# 通用 HTTP 数据源 API 协议

## 协议说明

蓝鲸用户管理内置了对通用 HTTP 数据源的插件支持，用户需要在服务方提供 `用户数据` 及 `部门数据` API，具体请求参数 & 响应规范如下。

## 鉴权模式

通用 HTTP 插件目前支持使用 `BearerToken` 或 `BasicAuth` 进行鉴权，后续将陆续支持其他鉴权方式。当前示例请求等效于：

```shell
# BearerToken
curl -H 'Authorization: Bearer ${BearerToken}' http://bk.example.com/apis/v1/users?page=1&page_size=100

# BasicAuth
curl -H "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=" http://bk.example.com/apis/v1/departments?page=1&page_size=100
```

## 用户数据 API

### Request 参数

| 参数名称     | 描述     | 必须支持   | 默认值 |
|------------|----------|----------|-------|
| page       | 页码      | ✓        | 1     |
| page_size  | 每页数量   | ✓        | 100   |

### Response 规范

```json5
{
    "count": 3,    // 总数量
    "results": [
        {
            "id": "100",                 // 用户（本数据源内）唯一 ID
            "username": "sanzhang",      // 用户名（英文名）
            "full_name": "张三",          // 用户全名（姓名）
            "email": "1234567891@qq.com", // 邮箱
            "phone": "12345678901",      // 手机号码
            "phone_country_code": "86",  // 手机区号
            "extras": {                  // 自定义字段信息
                "gender": "male"
            },
            "leaders": [],               // 用户直接上级唯一 ID
            "departments": ["company"]   // 用户所属部门唯一 ID
        },
        {
            "id": "101",
            "username": "sili",
            "full_name": "李四",
            "email": "1234567892@qq.com",
            "phone": "12345678902",
            "phone_country_code": "86",
            "extras": {
                "gender": "female"
            },
            "leaders": ["100"],
            "departments": ["dept_a"]
        },
        {
            "id": "102",
            "username": "wuwang",
            "full_name": "王五",
            "email": "1234567893@qq.com",
            "phone": "12345678903",
            "phone_country_code": "86",
            "extras": {
                "gender": "male"
            },
            "leaders": ["100", "101"],
            "departments": ["center_aa"]
        }
    ]
}
```

## 部门数据 API

### Request 参数

| 参数名称     | 描述     | 必须支持   | 默认值 |
|------------|----------|----------|-------|
| page       | 页码      | ✓        | 1     |
| page_size  | 每页数量   | ✓        | 100   |

### Response 规范

```json5
{
    "count": 3,  // 总数量
    "results": [
        {
            "id": "company",  // 部门（当前数据源内）唯一 ID
            "name": "总公司",  // 部门展示用名称
            "parent": null    // 父部门唯一 ID，若为根部门则为 null
        },
        {
            "id": "dept_a",
            "name": "部门A",
            "parent": "company"
        },
        {
            "id": "center_aa",
            "name": "中心AA",
            "parent": "dept_a"
        }
    ]
}
```

> 注意：蓝鲸用户管理将通过分页的方式，分多次拉取全量用户 & 部门数据；若指定范围超过总数量，则返回结果中 results 字段需为空列表。

### 描述

批量查询部门信息

### 输入参数

| 参数名称           | 参数类型   | 必选 | 描述                      |
|----------------|--------|----|-------------------------|
| department_ids | string | 是  | 部门 ID，多个以逗号分隔，限制数量为 50  |
| with_org_path  | bool   | 否  | 是否返回部门的组织路径，默认为 `false` |

### 请求示例

```
// URL Query 参数
department_ids=4,5&with_org_path=true
```

### 状态码 200 的响应示例

```json5
{
    "data": [
        {
            "id": 4,
            "name": "中心AA",
            "organization_path": "公司/部门A",
        },
        {
            "id": 5,
            "name": "中心AB",
            "organization_path": "公司/部门A",
        }
    ]
}
```

### 响应参数说明

| 参数名称              | 参数类型   | 描述                                         |
|-------------------|--------|--------------------------------------------|
| id                | int    | 部门唯一标识                                     |
| name              | string | 部门名称                                       |
| organization_path | string | 部门组织路径，格式为：`部门1/部门2/.../部门n`               |

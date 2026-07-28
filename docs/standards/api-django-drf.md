# 前后端接口规范（Django REST）

<!--
  本文档由通用骨架结合 bk-user 项目实际生成（Level 2 降级：无对应协议精确预设）。
  部分条目标注 <!-- TODO --> 待团队补充。
-->

> 适用于 bk-user 对外/对内的 HTTP JSON 接口（DRF）。接口契约以 DRF Serializer 为事实源，文档由 drf-yasg 自动生成。

---

## 一、架构概述

### 1.1 API 分组与受众

| 子模块 | 路由前缀 | 受众 | 认证方式 |
|--------|---------|------|---------|
| web | `/api/v3/web/` | 管理端 / 个人中心前端 | Cookie `bk_token` → LoginMiddleware → DRF Session |
| login | `/api/v3/login/` | bk-login 内部调用 | App Code/Secret（BkUserAppAuthentication） |
| apigw | `/api/v3/apigw/` | API 网关内部调用 | — |
| open_v3 | `/api/v3/open/` | 对外 OpenAPI | APIGateway JWT（ApiGatewayJWTAuthentication） |
| open_web | `/api/v3/open-web/` | 前端使用的开放 API | — |
| open_v1 / open_v2 | `/api/v1/` `/api/v2/` | 兼容旧版 ESB OpenAPI | — |

### 1.2 技术栈分工

| 层级 | 技术 | 职责 |
|------|------|------|
| 接口定义 | DRF Serializer | 入参/响应的单一事实源与校验 |
| 后端服务 | DRF View + biz Handler | 参数校验 → 业务编排 |
| API 文档 | drf-yasg（Swagger/OpenAPI） | 自动生成接口文档 |
| 前端请求 | axios（`src/pages/src/http`） | 类型安全调用，详见前端规范 |

---

## 二、接口定义规范

### 2.1 文件组织

- 按业务域拆分：`apis/web/<domain>/{views.py, serializers.py, urls.py}`。
- 子模块之间遵循 import-linter 独立性契约，互不 import（仅 `views -> serializers` 例外）。

### 2.2 URL 设计

| 规则 | 说明 | 示例 |
|------|------|------|
| 资源用名词复数 | RESTful 风格 | `/api/v3/web/data-sources/` |
| 版本号在路径 | 便于迁移 | `/api/v3/`、`/api/v1/` |
| 按受众分组 | web / open / login / apigw | 见 §1.1 |
| 命名连字符 | URL 段使用 `kebab-case` | `personal-center` |

---

## 三、数据类型约定

- 时间统一 ISO 8601 / RFC 3339；服务端存储 UTC，展示时转换。
- 大整数注意前端精度，必要时序列化为字符串。
- 空集合序列化为 `[]`，不用 `null`。
- 字段命名 `snake_case`（后端）；前端 bridge 层可转 camelCase。
<!-- TODO: 待确认——是否统一大整数序列化策略 -->

---

## 四、响应与错误格式

### 4.1 成功响应

以 DRF 默认结构为基础，具体以 `common/renderers` 与各 serializer 为准。

### 4.2 错误响应

- 错误码集中定义于 `bkuser/common/error_codes`。
- 异常经 DRF `exception_handler` 转换为标准错误结构（含错误码与可读 message）。
- **禁止**在响应中泄露堆栈、内部路径或敏感信息。

### 4.3 分页

- 使用 `common` 提供的分页类，返回列表项与总数；不在 view 内自造分页协议。
<!-- TODO: 待补充——固定分页字段命名（如 count/results 或 items/total）以实际实现为准 -->

---

## 五、前端接入

前端接口调用集中在 `src/pages/src/http/`，维护对应类型；不在组件内散落请求封装。详见 `src/pages/AGENTS.md` 与 `docs/standards/frontend-vue3.md`。

---

## 六、接口变更管理

| 规则 | 说明 |
|------|------|
| 禁止删除已发布字段 | 标记废弃代替删除 |
| 新增字段可选 | 保持向后兼容 |
| 破坏性变更走新版本 | 通过 `/api/vN/` 新路径 |
| 变更同步文档 | Serializer 变更即接口契约变更，同步 drf-yasg 文档与相关前端类型 |

### 完工标准

- [ ] Serializer 校验完整，认证/权限正确
- [ ] mypy / ruff / import-linter 通过
- [ ] 相关单元测试通过（`tests/apis/`）
- [ ] 安全红线核查通过
- [ ] 接口文档（drf-yasg）与前端类型已同步

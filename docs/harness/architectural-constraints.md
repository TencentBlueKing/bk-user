# 架构约束（Architectural Constraints）

> 目标：让 Agent "做正确的事"——通过刚性约束确保代码结构的一致性和可维护性。
>
> 本项目的分层约束由 `src/bk-user/pyproject.toml` 的 **import-linter** 契约强制，并纳入 pre-commit 与 CI。本文档是这些契约的人类可读解释，**修改分层时须同步更新契约与本文档**。

## 1. 分层架构模型

### 1.1 后端主分层（bkuser 顶层）

```text
apis / auth / monitoring （最上层，面向请求）
  ↓
biz          （业务编排）
  ↓
apps         （Django App：models / migrations / signals / tasks）
  ↓
plugins      （数据源插件）
  ↓
component    （外部系统 HTTP 客户端）
  ↓
common       （横切基础设施：error_codes / pagination / renderers / middlewares）
  ↓
utils        （最底层，纯工具函数，无外部依赖）
```

对应 `Layers contract`（root_package = `bkuser`）。

### 1.2 依赖规则

- 依赖只能**向下**流动：上层可 import 下层，下层**不得**引用上层。
- 同一层级组（如 `apis | auth | monitoring`）内部模块之间**不得**互相依赖。
- 对外部系统（bk-login、API 网关、ESB、CMSI 等）的调用必须经 `component/`，**禁止**在 `apis/`、`biz/` 内直接使用 `requests`。
- 例外仅限契约中显式 `ignore_imports` 声明的条目（如管理命令 `apps.tenant.management.commands.* -> biz.tenant`），新增例外须在契约中登记并说明理由。

### 1.3 子分层契约

| 契约 | 范围 | 层次（自上而下） |
|------|------|-----------------|
| Apps Layers | `bkuser.apps` 内部 | `sync \| permission` → `notification` → `tenant` → `idp` → `data_source` |
| Apps sync Layers | `bkuser.apps.sync` 内部 | `periodic_tasks` → `managers` → `tasks` → `runners` → `syncers` → `models` |
| Biz Layers | `bkuser.biz` 内部 | `tenant` → `data_source \| organization \| exporters` → `validators` |

### 1.4 独立性契约

| 契约 | 互不 import 的模块 | 例外 |
|------|-------------------|------|
| Apis Independence | `apis.login`、`apis.open_v2`、`apis.web` | 无 |
| Apis Web Independence | `apis.web.basic`、`apis.web.data_source`、`apis.web.organization`、`apis.web.platform_management` | `apis.web.*.views -> apis.web.*.serializers` |

### 1.5 目录与层次映射

| 层 | 目录 | 职责 | 允许的依赖 |
|----|------|------|-----------|
| apis | `bkuser/apis/` | DRF views / serializers / urls，参数校验与响应组装（薄） | biz、apps、common、utils |
| auth | `bkuser/auth/` | 用户认证（`TokenBackend`、`LoginMiddleware`） | component 及以下 |
| biz | `bkuser/biz/` | 跨 model 业务编排（Handler / Manager / 校验 / 导出，厚） | apps 及以下 |
| apps | `bkuser/apps/` | models / migrations / signals / Celery tasks | plugins 及以下 |
| plugins | `bkuser/plugins/` | 数据源插件（local / ldap / general） | component 及以下 |
| component | `bkuser/component/` | 外部系统 HTTP 客户端（login / esb / cmsi / apigw） | common、utils |
| common | `bkuser/common/` | error_codes / pagination / renderers / middlewares | utils |
| utils | `bkuser/utils/` | 纯工具函数 | 无 |

> `idp_plugins`（认证源插件）通过软链作为独立包被各层引用；配置侧在 bk-user，运行时认证在 bk-login。

### 1.6 双服务边界

- **bk-user**：用户 / 租户 / 数据源 / IdP 配置管理、数据同步、对外提供用户数据 OpenAPI。
- **bk-login**：统一登录入口、IdP 认证执行、`bk_token` 签发与校验、登录页 UI。
- 交互：bk-login → bk-user 走 `/api/v3/login/` 内部 API（App Code/Secret）；bk-user → bk-login 走 `component/login.py` 校验 `bk_token`（避免经网关形成循环依赖）。

## 2. 约束检查（Linter 规则）

### 2.1 规则清单

| 规则 | 工具 | 描述 | 修复指引 |
|------|------|------|---------|
| ARCH-LAYERS | import-linter `Layers contract` | 禁止下层引用上层、禁止同层互引 | 将被引用逻辑下沉，或在上层编排；确需例外则在契约 `ignore_imports` 登记 |
| ARCH-APPS | import-linter `Apps Layers` | apps 内部违反 sync/permission→…→data_source 顺序 | 调整调用方向或下沉共享逻辑 |
| ARCH-INDEP | import-linter `Apis * Independence` | apis 子模块互相 import | 通过 biz 层编排，或抽取公共逻辑到下层 |
| ARCH-EXTERNAL | 约定（评审核查） | apis/biz 直接调用外部 HTTP | 封装为 `component/` 下客户端后再调用 |

### 2.2 错误信息格式

import-linter 报错示例及修复方向：

```text
Layers contract BROKEN:
  bkuser.component.login is not allowed to import bkuser.biz.tenant
修复方式：component 层不得反向依赖 biz。将所需数据由上层（biz/apis）传入，
        或把 biz 中被依赖的纯逻辑下沉到 common/utils。
参考文档：docs/harness/architectural-constraints.md#依赖规则
```

## 3. Parse, Don't Validate

### 3.1 原则

在数据进入系统的边界处，将原始输入**解析**为强类型模型，后续代码只操作解析后的类型。

### 3.2 数据边界

| 边界 | 输入类型 | 解析目标 | 处理位置 |
|------|---------|---------|---------|
| Web / OpenAPI 请求 | JSON / Form | DRF Serializer 校验后的 `validated_data` | apis 层 serializers |
| 插件 / 组件配置 | dict / JSON | pydantic 模型 | plugins / component 层 |
| 外部接口响应 | JSON | 领域对象 | component 层客户端 |
| 环境变量 / 配置 | str | settings 类型化配置 | 启动阶段 `settings.py` |

- apis 层完成校验后向下传递已解析的数据；biz 层默认视输入为"已知有效"，不重复裸校验。

## 4. 架构决策记录（ADR）

### 4.1 管理方式

- 建议存储位置：`docs/adr/`，命名 `NNNN-标题.md`（如 `0001-采用-import-linter-固化分层.md`）。
- Agent 做出架构决策前，先检索已有 ADR，确保不与历史决策冲突。<!-- TODO: 待补充——当前仓库尚无 docs/adr/ 目录，按需建立 -->

### 4.2 ADR 模板

```text
# NNNN. 决策标题

## 状态：已接受 / 已废弃 / 已替代

## 背景
为什么需要做这个决策？

## 决策
选择了什么方案？

## 后果
带来了哪些影响（正面和负面）？
```

## 检查清单

- [ ] 分层依赖方向明确，与 import-linter 契约一致
- [ ] 新增跨模块引用前已确认不违反 Layers / Independence 契约
- [ ] 外部系统调用均封装在 `component/`
- [ ] 数据边界处执行 Parse（Serializer / pydantic / 类型化 settings）
- [ ] 修改分层时同步更新 `src/bk-user/pyproject.toml` 契约与本文档

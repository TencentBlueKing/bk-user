# 词汇表（Glossary）

> 本项目涉及的核心概念、术语和缩写定义。Agent 和人类成员均以此为术语的唯一解释来源。

## Harness Engineering 核心概念

| 术语 | 英文 | 定义 |
|------|------|------|
| 驾驭工程 | Harness Engineering | 为 AI Agent 构建可靠"运行环境"的工程实践，通过系统级工具链解决状态管理、工具调用、任务漂移与结果验证 |
| 上下文工程 | Context Engineering | 确保 Agent 在任务执行中获取准确、及时、适量的上下文 |
| 架构约束 | Architectural Constraints | 通过刚性规则（本项目由 import-linter 强制）保证代码结构一致性 |
| 熵管理 | Entropy Management | 通过自动化机制控制系统熵增，确保长期可维护 |
| 工具能力 | Tooling | 封装标准化工具接口，保障 Agent 执行的稳定性 |
| 执行与验证 | Execution & Verification | 通过执行循环与强制验证确保任务被正确完成 |

## 架构与设计模式

| 术语 | 英文 | 定义 |
|------|------|------|
| 分层契约 | Layers Contract | import-linter 定义的分层依赖约束，依赖只能自上而下流动 |
| 独立性契约 | Independence Contract | import-linter 约束一组模块之间互不 import |
| 解析而非校验 | Parse, Don't Validate | 在系统边界一次性将原始数据解析为强类型，后续代码只处理已知有效数据 |
| 架构决策记录 | ADR (Architecture Decision Record) | 记录架构决策的背景、方案与后果 |

## 业务领域术语

| 术语 | 英文/缩写 | 定义 |
|------|----------|------|
| 用户管理 | bk-user | 蓝鲸用户管理，提供组织架构与用户管理能力的后端服务 |
| 统一登录 | bk-login | 蓝鲸统一登录服务，执行认证并签发校验 bk_token |
| 租户 | Tenant | 多租户体系下的组织隔离单元 |
| 数据源 | Data Source | 用户 / 部门数据的来源（本地、OpenLDAP、MAD、Excel 等），由数据源插件同步 |
| 认证源 | IdP (Identity Provider) | 登录认证的身份提供方（本地、企业微信、OAuth/OIDC/SAML 等），由认证源插件实现 |
| 数据同步 | Data Source Sync | 从数据源拉取用户/部门数据并入库的过程（`apps/sync`） |
| 自然人 | Natural User | 跨租户/数据源关联同一现实个体的抽象（`apps/natural_user`） |
| bk_token | bk_token | 蓝鲸统一登录签发的登录态令牌，经 Cookie 传递，由 bk-login 校验 |

## 工具与平台

| 术语 | 英文/缩写 | 定义 |
|------|----------|------|
| Django REST Framework | DRF | 基于 Django 的 REST API 框架，本项目 API 层核心 |
| Celery | Celery | 分布式异步任务队列，用于数据同步等后台任务 |
| import-linter | import-linter | 校验 Python 模块导入是否符合分层契约的工具 |
| ruff | ruff | Python 代码格式化与 lint 工具（v3 有效） |
| mypy | mypy | Python 静态类型检查工具 |
| uv | uv | Python 依赖与版本管理工具 |
| TAPD | TAPD | 腾讯敏捷研发协作平台，需求 / 迭代管理来源 |
| API 网关 | APIGateway | 蓝鲸 API 网关，open_v3 经其 JWT 认证 |
| ESB | ESB | 蓝鲸企业服务总线，兼容旧版 OpenAPI（open_v1/v2）入口 |

## 工程实践术语

| 术语 | 英文 | 定义 |
|------|------|------|
| 渐进式上下文披露 | Progressive Disclosure | 分层组织文档，Agent 从入口逐层深入，控制上下文预算 |
| 唯一知识来源 | Single Source of Truth | 每类知识只有一个权威存储位置 |
| 预完成检查清单 | Pre-Completion Checklist | Agent 宣称完成前强制执行的验证项 |
| 文档园艺 | Documentation Gardening | 定期扫描文档与代码/规范的一致性并修复 |
| 提交门禁 | Pre-commit Gate | 提交前自动执行 ruff / mypy / import-linter 的强制检查 |

---

*持续补充中——遇到新术语时请直接在对应分类下添加。*

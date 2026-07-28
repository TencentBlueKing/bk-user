# 上下文工程（Context Engineering）

> 目标：让 Agent "知道该知道的信息"——确保 Agent 在任务执行中能获取准确、及时、适量的上下文。

## 1. 知识来源定义

### 1.1 唯一知识来源（Single Source of Truth）

| 知识类型 | 存储位置 | 说明 |
|---------|---------|------|
| 项目入口与全貌 | `AGENTS.md` | Agent 认知第一站 |
| 架构约束 | `docs/harness/architectural-constraints.md` | 与 `src/bk-user/pyproject.toml` 的 import-linter 契约同源 |
| 安全规范 | `docs/standards/security-bk-redlines.md` | 蓝鲸代码安全三大红线（横切必选） |
| 代码评审规范 | `docs/standards/quality-code-review.md` | 评审准则（横切必选） |
| 前端规范 | `docs/standards/frontend-vue3.md` | Vue 3 + TS 开发规范 |
| 后端规范 | `docs/standards/backend-django.md` | Django + DRF + Celery 分层与编码规范 |
| 接口规范 | `docs/standards/api-django-drf.md` | `/api/v3/` REST 接口协议规范 |
| 本地开发部署 | `docs/develop_guide.md` | 环境配置、迁移、启动命令 |
| 提交规范 | `docs/contributing.md` | Git 提交标记与关联 TAPD 的格式 |
| 词汇表 | `docs/glossary.md` | 术语的唯一解释来源 |

### 1.2 禁止的知识来源

以下渠道的信息不应作为 Agent 决策依据（容易过时或缺乏版本控制）：

- 即时通讯记录（企业微信、飞书等）
- 未纳入版本控制的外部 Wiki（iWiki 页面可作参考，但落地规则须回写仓库文档）
- 口头约定或会议记录
- 项目根 `pyproject.toml` 中面向旧 v2（`src/api`、`src/saas`）的 black/isort/flake8 配置——**已废弃**，v3 以各服务 `src/bk-user`、`src/bk-login` 下 `pyproject.toml` 的 ruff/mypy 为准

## 2. 渐进式上下文披露

### 2.1 三层结构

```text
第一层（入口）：AGENTS.md（≤100 行）
  ├── 项目概述、目录结构（二级）
  ├── 关键规范导航 + 核心架构约束
  └── 开发工作流入口

第二层（导航）：docs/harness/README.md + docs/standards/README.md
  ├── 五大组件导航
  ├── 技术规范导航 + Agent 加载策略
  └── 各文档控制在合理长度

第三层（详情）：各组件文档 + 各 standards 文档 + 源码内注释
  └── 仅在需要时访问，不主动全量加载到上下文
```

### 2.2 上下文预算管理

- Agent 的上下文窗口视为有限资源，优先加载与当前任务直接相关的文档。
- 后端任务：先看 `architectural-constraints.md` 确认分层，再定位到 `src/bk-user/bkuser/<layer>/<module>/`。
- 前端任务：以 `src/pages/AGENTS.md` 为准，其对前端约定描述更细。
- 大目录（如 `bkuser/apis/web/`）通过 `urls.py` 与子模块目录索引定位，避免全量读取。

## 3. 动态上下文接入

### 3.1 实时数据源

| 数据源 | 接入方式 | 用途 |
|-------|---------|------|
| TAPD 需求/迭代 | `tapd` MCP（tql/stories_get 等） | 需求澄清、评估、迭代规划与执行 |
| 数据库结构 | Django models（`bkuser/apps/*/models.py`） | 领域模型的事实源 |
| 接口契约 | DRF serializers + drf-yasg（`/swagger`） | API 结构与文档 |

### 3.2 可观测性数据

| 数据类型 | 工具 | 访问方式 |
|---------|------|---------|
| 健康检查 | `bkuser/monitoring/`（ping / healthz） | HTTP 探活接口 |
| 性能指标 | django-prometheus / Prometheus metrics | `/metrics` 端点 |
| 链路追踪 | OpenTelemetry | settings 中按需启用 |
| 异常上报 | Sentry | settings 中按需启用 |

## 4. 上下文更新机制

### 4.1 触发条件

- 后端分层或 import-linter 契约发生变更（`src/bk-user/pyproject.toml`）
- `/api/v3/` 接口新增或变更
- 数据源 / 认证源插件机制调整
- 依赖的外部系统（bk-login、API 网关、ESB）交互方式变更

### 4.2 更新流程

1. 变更方在 PR 中同步更新相关文档（架构变更须同步 `architectural-constraints.md`）。
2. Code Review 时检查文档是否同步更新（见 `quality-code-review.md`）。
3. 通过 harness-engineering "文档巡检" 定期扫描检测遗漏。

## 检查清单

- [ ] 所有知识类型都有明确的存储位置
- [ ] `AGENTS.md` 控制在 100 行以内
- [ ] 动态数据源（TAPD MCP、models、DRF 契约）已明确接入方式
- [ ] 上下文更新机制已建立，纳入 PR / Code Review 流程

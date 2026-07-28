# 工具能力（Tooling）

> 目标：让 Agent "能行动"——封装标准化工具接口，保障执行稳定性。
>
> 本文件的 Skill 清单由扫描 `.cursor/skills/*/SKILL.md`（仅顶层）并与治理仓 `tool-dependencies.md` 交叉验证生成；MCP / CLI 依赖以 `tool-dependencies.md` 为权威来源。

## 1. 工具清单

### 1.0 Skill 清单与触发

> Skill 即 Agent 可调用的工具能力。以下仅列出已在权威清单 `tool-dependencies.md` 登记的 Skill；用户额外安装的其他本地 Skill（如 code-review-expert、doc-to-todo、git-local-exclude）不在此登记。

| Skill | 触发词（示例） | 功能概要 |
|-------|--------------|---------|
| harness-engineering | Harness 规范、文档巡检、开发地图、词汇表 | 为 Agent 构建运行环境规范：规范文档生成 / 修正 与文档一致性巡检 |
| tapd-story-clarification | 需求澄清、clarify story | 从 TAPD 提取需求，按研发最佳实践多维度澄清并回写规范需求文档 |
| tapd-story-evaluation | 需求评估、需求拆分、RICE 评分 | 需求逻辑分析、子需求拆分与 RICE 价值规模评分 |
| tapd-iteration-plan | 迭代规划、排迭代、创建迭代 | 基于依赖关系与规模评分，将需求编排进入迭代 |
| tapd-iteration-runner | 迭代执行、开发迭代、批量需求实现 | 批量开发一个迭代的全部需求，编排四阶段流水线 |
| tapd-story-pipeline | 需求实现、实现需求 #ID、开发需求 | 单需求从澄清到提交的六阶段实现流水线 |

### 1.1 MCP 工具

> 权威清单：`.cursor/skills/harness-engineering/references/tool-dependencies.md` §一。变更先改权威清单，再重新运行规范生成。

| MCP 名称 | 所需接口 | 必需 | 环境状态 |
|---------|---------|------|---------|
| tapd | `stories_get` / `stories_create` / `stories_update` / `iterations_get` / `iterations_create` / `tapd_id_get` | 是 | ✅ 已就绪 |
| gongfeng | Issue / MR / 提交查询 | 否 | 未接入（依赖方 issue-* 系列 Skill 未安装，本仓暂不需要） |
| bkm-bkte | metrics / logs / dashboards / tracing 等 | 否 | 未接入（依赖方 sre-engineer 未安装，本仓暂不需要） |

**维护规则：** 禁止在本节手写与 `tool-dependencies.md` 冲突的条目；变更先改权威清单。

### 1.2 CLI 工具

| 工具 | 必需 | 检测条件 | 环境状态 |
|------|------|---------|---------|
| `git` | 是 | 始终 | ✅ 已安装 |
| `bash` | 是 | 始终 | ✅ 已安装 |
| `jq` | 是 | 始终（迭代报告 JSON 解析） | ✅ 已安装 |
| `node` | 否 | `package.json` 存在（前端 `src/pages`） | ✅ 已安装 |
| `python3` | 否 | 成本采集 hook（可选） | ✅ 已安装 |
| `graphify` | 否 | dev-map 生成时 | ❌ 未安装（开发地图功能跳过） |

### 1.3 配置文件依赖

| 文件 | 依赖方 | 必需 | 环境状态 |
|------|-------|------|---------|
| `project.json`（含 `workspace_id`、可选 `owner`） | tapd-story-* / tapd-iteration-* 系列 | 是 | ❌ 缺失（TAPD 系列 Skill 运行前需在仓库根目录补齐） |

### 1.4 项目专属技术栈工具（非 Skill 依赖，供参考）

| 工具 | 用途 | 说明 |
|------|------|------|
| `uv` | 后端依赖管理 | `uv sync --dev`（`src/bk-user`、`src/bk-login`） |
| `ruff` / `mypy` / `import-linter` | 后端 lint / 类型 / 分层 | 经 pre-commit 执行 |
| `pre-commit` | 提交门禁 | `pre-commit install` 后每次提交自动执行 |
| `pytest` / `pytest-django` | 后端测试 | `make test`（`--reuse-db`） |
| `npm` + `@blueking/cli-service-webpack` | 前端构建 | 见 `src/pages/AGENTS.md` |

## 2. 工具接口规范

### 2.1 统一调用协议

- **输入**：结构化参数（JSON），区分必填与可选。
- **输出**：结构化结果，含 `success` / `data` / `error`。
- **错误处理**：返回明确的错误码与可读信息。

后端自有接口遵循 DRF + `common/error_codes` 的统一错误格式，详见 `docs/standards/api-django-drf.md`。

## 3. 稳定性保障

### 3.1 沙盒执行

| 执行环境 | 隔离方式 | 适用场景 |
|---------|---------|---------|
| Shell 沙盒 | 文件系统限制在项目目录内 | 日常命令执行 |
| Docker 容器 | 完全隔离 | 服务构建 / 部署（各服务 `Dockerfile`） |

### 3.2 容错策略

| 策略 | 说明 |
|------|------|
| 超时 | 所有外部调用（component / MCP）配置超时 |
| 重试 | 网络请求指数退避，最多 3 次 |
| 幂等 | 写操作在相同参数下结果一致 |
| 降级 | 非关键工具（如 graphify）不可用时跳过对应能力 |

### 3.3 敏感操作防护

| 操作类型 | 防护措施 |
|---------|---------|
| 删除文件 / 目录 | 二次确认 |
| 提交敏感信息（.env、Token、Cookie、真实账号、内部地址） | 严格禁止提交 |
| 访问生产环境 | 严格禁止 / 需特殊授权 |
| 执行数据库迁移 | 审慎，附回滚方案（`python manage.py migrate`） |

## 4. 工具扩展规范

1. 新增 Skill 后，更新治理仓 `tool-dependencies.md`，并重新运行 harness-engineering 同步本清单。
2. 新增 MCP 依赖时，先在权威清单 §一 登记。
3. 工具文档与代码同仓库版本控制。

## 检查清单

- [ ] Skill 清单与 `.cursor/skills/*/SKILL.md`（登记项）一致
- [ ] 所有「必需」工具在环境中已就绪（tapd MCP、git/bash/jq）
- [ ] MCP 清单与 `tool-dependencies.md` §一 一致
- [ ] 环境缺口（`project.json`、graphify）已在总结报告中说明
- [ ] 敏感操作防护措施已明确

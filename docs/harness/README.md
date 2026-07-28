# Harness Engineering 规范

> 本目录定义了项目的 AI Agent 运行环境规范，是 Agent 理解项目边界、工具能力和行为约束的唯一来源。

## 项目概述

- **项目名称**：蓝鲸用户管理（bk-user）
- **技术栈**：Django 4.2 + Django REST Framework + Celery + MySQL + Redis（后端）；Vue 3 + TypeScript（前端）；uv / poetry 管理依赖
- **Agent 适用场景**：TAPD 需求驱动的迭代研发（澄清 → 评估 → 规划 → 实现 → 校验 → 提交）、代码评审与安全检查、文档巡检

## 规范导航

| 组件 | 文档 | 概要 |
|------|------|------|
| 上下文工程 | [context-engineering.md](context-engineering.md) | 知识来源、渐进式上下文披露、动态数据接入 |
| 架构约束 | [architectural-constraints.md](architectural-constraints.md) | import-linter 分层模型、依赖规则、Parse-Don't-Validate |
| 熵管理 | [entropy-management.md](entropy-management.md) | 文档园艺、pre-commit 门禁、技术债追踪 |
| 工具能力 | [tooling.md](tooling.md) | Skill 清单、MCP/CLI 工具、环境状态、稳定性保障 |
| 执行与验证 | [execution-verification.md](execution-verification.md) | 执行循环、预完成检查清单、任务漂移检测 |

## 相关规范

- 技术开发规范（安全 / 质量 / 前端 / 后端 / 接口）→ [`../standards/README.md`](../standards/README.md)
- 词汇表 → [`../glossary.md`](../glossary.md)
- 迭代开发工作流 → [`../workflow.md`](../workflow.md)

## 使用说明

1. Agent 首次接触项目时，先读 `AGENTS.md` 获取全局视图，再按需深入本目录组件文档。
2. 执行具体任务时，按需加载对应组件文档；实现代码前必读 `architectural-constraints.md` 与 `../standards/README.md`。
3. 规范更新后需同步检查关联组件的一致性（尤其 `tooling.md` 与 Skill 清单、`architectural-constraints.md` 与 import-linter 契约）。

## 版本记录

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-07-28 | 初始版本 |

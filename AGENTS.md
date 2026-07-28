# AGENTS.md

> Agent 认知本项目的第一站——快速了解项目全貌、找到代码和规范、知道规矩。

## 项目概述

- **项目名称**：蓝鲸用户管理（bk-user）
- **仓库地址**：https://github.com/TencentBlueKing/bk-user
- **定位**：蓝鲸智云的企业组织架构与用户管理解决方案，为企业统一登录提供认证源服务。
- **目标**：多层级组织架构管理、多种数据源同步（OpenLDAP / MAD / Excel 等）、多认证源统一登录与账号安全策略。

## 目录结构

```text
src/
├── bk-user/     — 用户管理后端（Django 4.2 + DRF + Celery），核心 app 在 bkuser/
├── bk-login/    — 统一登录服务（Django，执行 IdP 认证、签发校验 bk_token，含前端）
├── idp-plugins/ — 认证源插件源码（软链到 bk-user 与 bk-login 消费）
└── pages/       — 用户管理前端（Vue 3 + TypeScript，见 src/pages/AGENTS.md）
docs/
├── harness/     — AI Agent 运行环境规范（五大组件）
├── standards/   — 技术开发规范（安全 / 质量 / 前端 / 后端 / 接口）
├── glossary.md  — 词汇表（核心概念与业务术语）
├── workflow.md  — 迭代开发工作流定义
└── *.md         — 架构、开发指引、贡献指南等参考文档
```

## 关键规范

- Harness 规范（工具能力、Skill 清单、架构约束、熵管理等）→ [`docs/harness/README.md`](docs/harness/README.md)
- 技术开发规范（安全红线、代码评审、前后端与接口规范）→ [`docs/standards/README.md`](docs/standards/README.md)
- 前端专属约定 → [`src/pages/AGENTS.md`](src/pages/AGENTS.md)
- 本地开发部署 → [`docs/develop_guide.md`](docs/develop_guide.md)；提交规范 → [`docs/contributing.md`](docs/contributing.md)

## 核心架构约束（务必遵守）

后端 `bkuser` 由 import-linter 强制分层，依赖只能自上而下流动，反向禁止：

```text
apis / auth / monitoring  →  biz  →  apps  →  plugins  →  component  →  common  →  utils
```

- views 层薄、biz 层厚；跨 model 的业务编排放 `biz/`，持久化与领域事件放 `apps/`。
- 对外部系统的 HTTP 调用统一走 `component/`，不在 apis/biz 内直接使用 requests。
- bk-login 负责认证执行，bk-user 负责用户数据，二者通过 `/api/v3/login/` 内部 API 协作。
- 详见 [`docs/harness/architectural-constraints.md`](docs/harness/architectural-constraints.md)。

## 开发工作流

本项目使用 `workflow-agent` 按 [`docs/workflow.md`](docs/workflow.md) 定义的步骤推进迭代开发。workflow-agent 启动时主动感知当前状态（首次执行、崩溃恢复、错误暂停、重新开始），无需用户输入特定指令。不允许跳过工作流步骤或自行决定开发流程。

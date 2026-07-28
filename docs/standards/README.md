# 技术规范

> Agent 实现需求时的开发行为准则。根据需求涉及的端按需加载对应规范。

## 必选规范（所有项目强制）

| 分类 | 规范 | 文档 |
|------|------|------|
| 安全 | 蓝鲸代码安全三大红线 | [security-bk-redlines.md](security-bk-redlines.md) |
| 质量 | 代码评审规范（Google Code Review 指南） | [quality-code-review.md](quality-code-review.md) |

> 安全规范为横切关注点，**无论需求类型、技术栈如何，每次 Code Review 均须核查**。

## 当前项目选用的规范

| 分类 | 规范 | 文档 | 技术栈 |
|------|------|------|--------|
| 前端 | Vue 3 + TypeScript | [frontend-vue3.md](frontend-vue3.md) | vue3 · typescript · pinia |
| 后端 | Django + DRF + Celery | [backend-django.md](backend-django.md) | python · django · drf · celery |
| 接口 | Django REST（`/api/v3/`） | [api-django-drf.md](api-django-drf.md) | django · drf · openapi |

## Agent 加载策略

| 需求类型 | 应加载的规范 |
|---------|------------|
| 任何需求 | 安全规范 + 代码评审规范（必选） |
| 涉及前端页面（`src/pages`、`src/bk-login/pages`） | 前端规范 + `src/pages/AGENTS.md` |
| 涉及后端逻辑（`src/bk-user`、`src/bk-login`） | 后端规范 + 架构约束 |
| 涉及接口定义 / 联调 | 接口规范 + 后端规范 |
| 全栈需求 | 加载全部规范 |

## 规范约束力

- 标注"禁止"/"必须"的条目：**强制**遵守，违反需明确说明原因。
- 标注"推荐"/"优先"的条目：**优先**遵守，有合理理由可偏离。
- 常见场景参考：**参考**实现，可根据具体情况调整。

## 章节快速索引

- **安全（security-bk-redlines）**：输入校验、认证鉴权、加密与敏感数据（三大红线）
- **质量（quality-code-review）**：评审关注点、设计/功能/复杂度、命名与注释、测试
- **前端（frontend-vue3）**：Vue 3 组件、Composition API、Pinia、i18n、请求分层、样式
- **后端（backend-django）**：技术栈、import-linter 分层、DRF/ORM 约定、Celery、测试、安全
- **接口（api-django-drf）**：API 分组与受众、URL 设计、响应/错误格式、分页、变更管理

## 待完善的规范

| 分类 | 当前状态 | 技术栈 | 如何完善 |
|------|---------|--------|---------|
| 后端 | 结构完整，含项目实际约定，部分细节标注待补充（Level 2） | Django/DRF/Celery | 补齐 TODO（覆盖率阈值等）；如需可编写完整预设放入 `assets/standards/` 并注册 `index.yaml` |
| 接口 | 结构完整，含项目实际约定，部分细节标注待补充（Level 2） | Django REST | 确认分页/大整数序列化等约定后补齐 TODO |

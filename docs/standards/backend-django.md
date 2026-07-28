# 后端开发规范（Django + DRF + Celery）

<!--
  本文档由通用骨架结合 bk-user 项目实际生成（Level 2 降级：无对应技术栈精确预设）。
  部分条目标注 <!-- TODO --> 待团队补充。如需完善为完整预设，可放入
  skills/harness-engineering/assets/standards/ 并注册 index.yaml 贡献回预设库。
-->

> 适用于 `src/bk-user`（bkuser）与 `src/bk-login`（bklogin）两个 Django 服务。分层约束以 `src/bk-user/pyproject.toml` 的 import-linter 契约为准，详见 `docs/harness/architectural-constraints.md`。

---

## 一、技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11（`>=3.11,<3.12`） | 运行时 |
| Django | 4.2.x | Web 框架 |
| Django REST Framework | 3.16.x | API 层（bk-user；bk-login 不使用 DRF，用原生 View + pydantic） |
| Celery | 5.5.x | 异步任务（仅 bk-user） |
| MySQL | pymysql 1.1.x | 主数据库 |
| Redis | redis 6.x + django-redis | 缓存 / Celery broker 默认回退 |
| uv | — | 依赖管理（`uv sync --dev`） |
| pydantic | — | 配置 / 插件数据解析 |

---

## 二、项目结构与分层

顶层分层（import-linter 强制，自上而下）：

```text
apis / auth / monitoring  →  biz  →  apps  →  plugins  →  component  →  common  →  utils
```

| 目录 | 职责 |
|------|------|
| `bkuser/apis/` | DRF views / serializers / urls，参数校验与响应组装（**薄**） |
| `bkuser/biz/` | 跨 model 业务编排：Handler / Manager / validators / exporters（**厚**） |
| `bkuser/apps/` | Django App：models / migrations / signals / Celery tasks |
| `bkuser/plugins/` | 数据源插件（local / ldap / general） |
| `bkuser/component/` | 外部系统 HTTP 客户端（login / esb / cmsi / apigw） |
| `bkuser/common/` | error_codes / pagination / renderers / middlewares / hashers |
| `bkuser/utils/` | 纯工具函数 |
| `bkuser/auth/` | 认证（TokenBackend / LoginMiddleware） |
| `bkuser/monitoring/` | ping / healthz / metrics / tracing |

### 依赖规则

- 依赖只能向下；下层禁止 import 上层，同层组内禁止互引。
- 外部系统调用一律封装到 `component/`，禁止在 apis/biz 内直接 `requests`。
- 新增例外须在 import-linter 契约 `ignore_imports` 登记并说明理由。

---

## 三、编码规范

### 3.1 工具链（v3 有效）

| 环节 | 工具 | 说明 |
|------|------|------|
| 格式化 + lint | ruff | 以各服务 `pyproject.toml` 为准；**不使用**根目录遗留的 black/isort/flake8 |
| 类型检查 | mypy | 提交前强制 |
| 分层校验 | import-linter | 提交前强制 |
| 圈复杂度 | ruff mccabe | `max-complexity = 10` |
| 提交门禁 | pre-commit | `pre-commit install` 后自动执行以上检查 |

> **禁止**使用 `git commit --no-verify` 跳过门禁。

### 3.2 命名与风格

| 元素 | 规则 |
|------|------|
| 模块 / 包 | 小写下划线 `snake_case` |
| 类 | `PascalCase` |
| 函数 / 方法 / 变量 | `snake_case` |
| 常量 | `UPPER_SNAKE_CASE` |
| 私有 | 前缀单下划线 `_name` |

- 遵循 Django/DRF 惯例；view 保持薄，业务逻辑放 biz。
- 注释使用中文，仅解释业务原因、边界条件与非显而易见的取舍。

---

## 四、Django / DRF 约定

| 主题 | 约定 |
|------|------|
| Serializer | 请求入参与响应统一用 Serializer 定义与校验；view 使用 `validated_data` |
| ORM | 查询集中在 biz/apps；注意 N+1，使用 `select_related`/`prefetch_related` |
| 迁移 | 模型变更须生成 migration；迁移文件纳入版本控制，附回滚考量 |
| 错误处理 | 使用 `common/error_codes` 统一错误码；异常经 DRF exception_handler 转标准响应 |
| 分页 | 使用 `common` 提供的分页类，不在 view 内自造 |
| 认证 / 权限 | 复用对应 apis 子模块的认证 mixin（web/open_v3/login/apigw）；不在业务代码里散写认证逻辑 |
| 事务 | 涉及多写操作使用 `transaction.atomic`，保证一致性 |
| 国际化 | 用户可见文案通过 gettext；同步维护 locale（`make i18n-*`） |

---

## 五、异步任务（Celery）

| 规则 | 说明 |
|------|------|
| 适用场景 | 数据同步、耗时/可重试/需状态追踪的操作 |
| 任务位置 | 定义在 `apps/*/tasks`；周期任务在 `apps/sync/periodic_tasks` |
| 幂等 | 任务应可安全重试，避免重复副作用 |
| 参数 | 传递可序列化的轻量标识（如 id），不传大对象 |
| 分层 | sync 内部遵循 `periodic_tasks → managers → tasks → runners → syncers → models` |

---

## 六、配置管理

| 规则 | 说明 |
|------|------|
| 环境变量优先 | 敏感配置（密钥、密码、App Secret）经 `.env` / 环境变量注入，见 `develop_guide.md` |
| 禁止提交敏感信息 | `.env`、Token、Cookie、真实账号、内部地址、生产数据一律不入库 |
| 类型化 | 在 `settings.py` 边界处解析并校验配置 |
| 默认值 | 配置项提供合理默认；缺失必填项应启动失败 |

---

## 七、测试规范

| 项 | 约定 |
|----|------|
| 框架 | pytest + pytest-django；`make test`（`pytest --reuse-db`） |
| 组织 | `tests/` 镜像源码分层（apis / apps / biz / common / plugins） |
| Fixture | 复用 `tests/fixtures/`、`tests/test_utils/`（create_tenant / create_user） |
| 覆盖 | 新增行为覆盖主路径、失败路径与关键边界 |
| 数据库 | 使用测试库，禁止连生产/开发库 |
<!-- TODO: 待补充——覆盖率门槛阈值由团队约定 -->

---

## 八、安全

安全为横切必查项，详见 `docs/standards/security-bk-redlines.md`。后端要点：

| 规则 | 说明 |
|------|------|
| 输入校验 | 所有外部输入经 Serializer / pydantic 校验 |
| 注入防护 | 使用 ORM / 参数化查询，禁止拼接 SQL |
| 认证鉴权 | 所有 API 经认证（公开接口除外），权限校验不可绕过 |
| 敏感数据 | 密码使用 hashers；日志/响应不暴露密钥与个人敏感信息 |
| 越权 | 多租户下严格校验租户边界，防止跨租户数据访问 |

---

## 九、构建与运行

| 命令 | 作用 |
|------|------|
| `uv sync --dev` | 安装依赖 |
| `python manage.py migrate` | 数据库迁移 |
| `./bin/start.sh` | 启动 Web 服务 |
| `./bin/start_celery.sh` / `start_celery_beat.sh` | 启动 Celery Worker / Beat（bk-user） |
| `make test` | 运行测试 |
| `make package-plugin name=<plugin>` | 打包自定义数据源插件（bk-user） |

详见 `docs/develop_guide.md` 与各服务 `Makefile`。

# AGENTS.md

## 适用范围

本文件适用于整个 `bk-user` 仓库。开始工作前，先确认目标文件所在子项目，并继续查找该目录下是否存在更近的 `AGENTS.md` 或 `AGENTS.override.md`；更近的规则优先。

用户在当前任务中的明确要求始终高于本文件。若规则、源码与文档不一致，以当前源码、子项目配置和 CI 工作流为准，并在交付结果中说明差异。

## 沟通与注释

- 默认使用中文沟通，命令、标识符、协议名和第三方专有名词保留原文。
- 新增或修改的代码注释使用中文，只解释业务原因、边界条件和非显而易见的取舍，不为直观代码添加重复注释。
- 延续所在文件已有的命名、类型标注、错误处理和代码组织方式，不进行与任务无关的风格改写。

## 仓库结构

- `src/bk-user/`：用户管理后端，Python 3.11、Django 4.2、Django REST Framework，使用 `uv`、Ruff、mypy、pytest 和 import-linter。
- `src/bk-login/`：统一登录后端，Python 3.11、Django 4.2；其前端位于 `src/bk-login/pages/`。
- `src/idp-plugins/`：登录与用户管理共同使用的 IDP 插件。这里的改动必须同时评估 `bk-user` 和 `bk-login` 两个消费者。
- `src/pages/`：用户管理前端，Vue 3、TypeScript、Pinia、Vue Router、Vue I18n 和 BKUI。
- `src/bk-login/pages/`：统一登录前端，Vue 3、TypeScript、Pinia、Vue Router、Vue I18n 和 BKUI。
- `docs/`：架构、开发、贡献和行为说明。面向用户或开发者的行为变化应同步更新对应文档。

根目录的 `Makefile` 和 `pyproject.toml` 包含历史工程路径与配置，不应自动当作当前子项目的唯一入口。执行命令前优先读取目标目录的 `README.md`、`Makefile`、`pyproject.toml` 或 `package.json`。

## 基本工作方式

1. 开始前运行 `git status --short`，识别用户已有改动；不得覆盖、回滚或格式化无关文件。
2. 先阅读相关实现、测试、配置和文档，再做最小范围修改。不要仅凭文件名或接口名称猜测行为。
3. 修复缺陷时优先补充能复现问题的回归测试；新增功能应覆盖主路径、失败路径和关键边界。
4. 优先复用现有组件、工具函数、异常类型和抽象。未经充分理由，不新增依赖、兼容层或平行实现。
5. 自动格式化和自动修复命令可能改写大量文件；只对本次涉及的文件或子项目执行，并在执行后立即检查 diff。
6. 未经用户明确要求，不创建提交、不推送分支、不发起 PR、不发布版本，也不执行破坏性数据库、部署或批量删除操作。
7. 交付前检查实际 diff，并明确列出已运行的验证、未运行项及原因。不要把环境缺失或仓库既有失败描述成本次改动回归。

## Git 提交规范

- 只有用户明确要求提交时才创建 commit。提交前必须核对 staged 范围，确保不包含用户的无关改动。
- commit message 格式为 `<标记>: <中文概要> [TAPD/Issue 关键字]`。标题概要和正文必须使用中文，标记与平台关键字保留规范原文。
- 关联 TAPD 时，将 `--story=<id>` 或 `--bug=<id>` 放在提交标题末尾，例如：`docs: 补充仓库级 AGENTS 开发规范 --story=136169792`。
- 一个提交只选择最符合主要改动性质的标记：

  | 标记 | 说明 |
  | --- | --- |
  | `feature` / `feat` | 新功能开发 |
  | `bug` / `fix` / `bugfix` | 缺陷修复 |
  | `refactor` / `perf` | 重构代码，或优化配置、参数、逻辑与性能 |
  | `test` | 新增或调整单元测试 |
  | `docs` | 文档变更 |
  | `info` | 注释或说明信息变更 |
  | `format` | 不修改业务逻辑的格式调整 |
  | `merge` | 仅用于分支合并同步 |
  | `depend` | 增删或调整工程依赖 |
  | `chore` | 构建脚本、任务及其他工程维护 |
  | `del` | 删除可能仍有调用方使用的功能或 API 等破坏性改动 |

- 提交后用 `git log -1 --pretty=format:'%H%n%s'` 核对最终标题；关联 TAPD 的提交必须确认关键字完整且位于标题末尾。

## 环境与依赖

### Python 子项目

- Python 版本为 `>=3.11,<3.12`，CI 使用 `uv 0.7.19`。
- `bk-user`、`bk-login` 和 `idp-plugins` 各自拥有独立的 `pyproject.toml` 与 `uv.lock`，必须在对应目录安装和执行命令。
- 常规安装命令为 `uv sync --locked --all-extras --dev`。只有任务明确需要调整依赖时才更新 `pyproject.toml` 和 `uv.lock`，并说明依赖变更原因。
- `idp_plugins` 通过软链接供两个后端使用。需要运行相关后端时，按 `docs/develop_guide.md` 创建链接：

  ```bash
  ln -s "$(pwd)/src/idp-plugins/idp_plugins" "$(pwd)/src/bk-login/bklogin"
  ln -s "$(pwd)/src/idp-plugins/idp_plugins" "$(pwd)/src/bk-user/bkuser"
  ```

  创建前先确认目标不存在；不要用强制覆盖方式替换用户已有目录或链接。

### 前端子项目

- 两个前端项目均使用 `package-lock.json`，安装依赖优先使用 `npm ci`，不要混用 Yarn 或 pnpm。
- `package.json` 中的 Node/npm engines 与当前 lockfile 版本可能存在历史差异。遇到安装失败时应报告版本信息并核对项目现有环境，不要仅为消除警告重写整个 lockfile。
- 依赖调整必须同步更新 `package.json` 与 `package-lock.json`。不要提交 `node_modules/`、构建目录或本地环境文件。

### 配置与敏感信息

- `.env`、密钥、Token、Cookie、真实账号、内部地址和生产数据不得写入源码、测试快照、日志或文档。
- 测试数据使用明显的虚构值；日志不得输出密码、访问令牌、认证回调参数或完整个人敏感信息。
- 不绕过权限、租户隔离、CSRF、输入校验或敏感字段脱敏来“临时修好”功能。

## 后端开发约定

- 遵守各子项目 `pyproject.toml` 中的 Ruff、mypy 和 import-linter 配置；Python 行宽为 119。
- `bk-user` 的模块依赖必须符合 `src/bk-user/pyproject.toml` 中定义的分层与独立性契约。不要通过延迟导入、路径修改或重复代码规避 import-linter。
- API 修改应保持兼容性；若必须改变字段、状态码或错误语义，应同步修改序列化、调用方、测试和文档，并明确指出破坏性影响。
- 涉及租户、数据源、组织和用户查询时，显式验证租户边界、权限范围、空数据、重复数据和批量数据场景，避免 N+1 查询及无界加载。
- 涉及事务与 Celery 任务时，关注重复执行、重试、并发、回滚及 `transaction.on_commit` 时机；不要在事务提交前发布依赖未提交数据的任务。
- Django 模型变化应生成新的迁移并检查迁移内容，不手工篡改已发布迁移。能连接开发环境时，执行 `makemigrations --check --dry-run` 和相关迁移测试。
- 用户可见文本使用 Django i18n；更新文案后同步维护对应 `.po`，需要交付编译产物时再运行子项目的 `make i18n-mo`。
- IDP 插件公共模块使用相对导入，以保证它同时挂载到 `bkuser` 与 `bklogin` 时可用；自定义插件 ID 遵循 `custom_` 前缀约定。

## 前端开发约定

- 优先使用 Vue 3 Composition API 与 TypeScript，保持组件职责单一；共享状态放入现有 Pinia store，共享请求逻辑放入现有 HTTP 层或 composable。
- 优先复用 bkui-vue 组件库和仓库已有组件、样式变量及交互模式，不重复实现通用控件。
- 为接口入参、返回值、组件 props 和 emits 提供明确类型。避免新增 `any`；确实无法避免时，缩小范围并用中文注释说明原因。
- 用户可见文本必须接入 Vue I18n，并同时更新 `zh.json` 与 `en.json`。不要在模板、通知或异常处理分支中散落硬编码文案。
- 不直接渲染不可信 HTML；确需使用 HTML 内容时，沿用项目现有的净化方案并验证 XSS 边界。
- 修改路由、权限、租户切换、登录回调或请求拦截逻辑时，验证刷新、直达 URL、未登录、无权限、请求失败和多语言场景。
- 样式修改应检查常见窗口宽度、长文本、空状态和中英文布局，不通过全局覆盖修复局部问题。

## 常用命令与验证矩阵

验证遵循“先最小相关范围，再按风险扩大”的顺序。命令均从对应子项目目录执行。

### `src/bk-user`

```bash
uv sync --locked --all-extras --dev
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run lint-imports
uv run pytest tests/path/to/test_file.py -q
```

完整后端测试可执行 `uv run pytest tests --maxfail=1 -l --reuse-db --disable-warnings -vv` 或 `make test`。

### `src/bk-login`

```bash
uv sync --locked --all-extras --dev
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run lint-imports
uv run pytest tests/path/to/test_file.py -q
```

完整后端测试可执行 `uv run pytest tests --maxfail=1 -l --reuse-db --disable-warnings` 或 `make test`。

### `src/idp-plugins`

```bash
uv sync --locked --all-extras --dev
uv run ruff format --check .
uv run ruff check .
uv run mypy .
```

修改共享插件后，还应在 `bk-user` 和 `bk-login` 中运行相关测试或至少完成导入与启动检查。

### `src/pages`

```bash
npm ci
npm run lint
npm run build
npm run i18n
```

`npm run lint:fix` 和 `npm run lint:style` 会修改文件，只在明确需要修复格式时运行，并在运行后检查无关改动。

### `src/bk-login/pages`

```bash
npm ci
npx eslint --ext .js,.vue,.ts ./src
npx stylelint "**/*.{html,vue,css,sass,scss,less}"
npm run build
```

该项目现有 `lint:fix` 与 `lint:style` 脚本都会修改文件，不能把它们当作只读检查命令。

### 通用检查

```bash
git diff --check
git status --short
git diff --stat
```

`pre-commit` 中包含自动格式化和 `--fix` 钩子。需要运行时优先限制到本次改动文件，并在运行前后分别检查 `git diff --name-only`。

## 文档、测试与生成文件

- 行为、配置、安装步骤、公开接口或运维方式变化时，更新距离该功能最近的 README 或 `docs/` 文档。
- 测试应断言对外行为，避免依赖执行顺序、真实时间、真实网络和共享外部状态。必要时使用已有 fixture、冻结时间或 mock。
- 不手工编辑 `uv.lock`、`package-lock.json`、Django 编译语言文件和其他生成产物；使用对应工具生成，并检查生成 diff 是否仅包含预期变化。
- 只改文档或规则文件时，无需运行完整业务测试，但至少执行通用检查并核对文档中的命令、路径确实存在。

## 完成标准

任务完成前确认：

- 改动严格落在用户要求的范围内，没有覆盖用户原有工作。
- 新行为有对应测试，或已说明无法添加/运行测试的具体原因。
- 已执行与改动风险相匹配的 lint、类型检查、测试或构建。
- 国际化、数据库迁移、锁文件、文档及两个共享消费者已按需同步。
- `git diff --check` 通过，最终 diff 中没有调试代码、敏感信息、大范围无关格式化或生成垃圾。
- 最终回复简要说明结果、关键文件、验证结果和剩余风险；不得把未执行的检查表述为已通过。

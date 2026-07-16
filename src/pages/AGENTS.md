# AGENTS.md

## 适用范围

本文件适用于 `src/pages/` 下的用户管理前端。用户在当前任务中的明确要求优先于本文件；若说明与源码或配置不一致，以当前 `package.json`、构建配置和实际代码为准。

开始工作前先执行 `git status --short`，识别并保留用户已有改动。只修改完成任务所必需的文件，不顺手格式化或重构无关代码。

## 项目概览

- 技术栈：Vue 3、TypeScript、Composition API、Pinia、Vue Router、Vue I18n、BKUI Vue、Less/CSS。
- 构建工具：`@blueking/cli-service-webpack`，入口为 `src/main.ts`。
- `src/views/`：业务页面；`src/components/`：可复用组件；`src/hooks/` 与 `src/composables/`：共享组合逻辑。
- `src/http/`：接口定义、类型和请求拦截；`src/store/`：Pinia 状态；`src/router/`：路由配置。
- `src/language/zh.json` 与 `src/language/en.json`：中英文文案；`src/css/`：全局样式。
- `paas-server/`、`mock-server/`、`bin/`：本地服务和构建脚本；非相关任务不要改动。

## 开发约定

- 优先延续相邻代码的组件组织、命名、类型和错误处理方式，不引入平行实现。
- 新增或修改的代码注释使用中文，只解释业务原因、边界条件和非显而易见的取舍。
- 组件优先使用 Composition API 和 TypeScript；保持职责单一，复杂逻辑抽到现有 hook、composable 或工具模块。
- 优先复用 `bkui-vue`、仓库已有组件和样式变量，不重复实现通用控件，不通过全局样式覆盖修复局部问题。
- 为接口入参、返回值、组件 props、emits 和共享状态提供明确类型；避免新增 `any`，确实无法避免时缩小范围并用中文注释说明原因。
- 用户可见文本必须通过 Vue I18n 获取，并同步维护 `zh.json` 与 `en.json`；不要在模板、通知或异常分支中新增硬编码文案。
- 接口调用统一放在 `src/http/` 现有分层中，同时维护对应类型；不要在组件内散落重复请求封装。
- 跨页面共享状态优先放入现有 Pinia store；仅组件内部使用的状态保持局部，不为简单状态新增全局 store。
- 修改路由、权限、租户切换、登录态或请求拦截时，检查刷新、直达 URL、未登录、无权限、接口失败和多语言场景。
- 不直接渲染不可信 HTML；确需展示 HTML 时沿用项目已有 `vue-dompurify-html` 方案并验证 XSS 边界。
- 表单和异步操作需处理重复提交、加载态、失败提示及组件卸载后的状态更新；批量列表逻辑需关注性能和空数据。
- 样式修改至少检查常见窗口宽度、长文本、空状态及中英文布局，避免使用脆弱的固定尺寸掩盖布局问题。

## 环境与依赖

- 使用 npm 管理依赖，不混用 Yarn 或 pnpm。
- 当前 `package-lock.json` 被子项目 `.gitignore` 忽略；不要擅自提交锁文件或调整忽略规则。依赖变更至少更新 `package.json`，并在交付中说明验证环境。
- 本地开发按 `README.md` 使用 `.bk.local.<env>.env`。不得提交本地环境文件、Token、Cookie、真实账号、内部地址或生产数据。
- 不提交 `node_modules/`、构建产物、缓存、日志及编辑器临时文件。
- 不为消除版本警告而批量升级依赖；新增依赖前先确认现有工具或依赖无法满足需求，并评估产物体积和浏览器兼容性。

## 常用命令

在 `src/pages/` 目录执行：

```bash
npm run dev
npm run dev --env=dev
npm run lint
npm run build
npm run i18n
```

- 优先运行与改动最相关的检查；涉及路由、构建配置、依赖或跨模块改动时再运行完整构建。
- `npm run lint:fix` 和 `npm run lint:style` 会修改文件，只在明确需要时执行，并立即检查 diff。
- 项目未定义单元测试脚本，不要声称测试已通过；无法自动验证的交互应说明手工验证范围。
- 仅修改 `AGENTS.md` 等规则文档时，无需运行完整业务构建，但至少执行 `git diff --check` 并核对文档中的命令和路径。

## Git 提交规范

- 只有用户明确要求时才创建 commit、push 或 PR；提交前必须核对 staged 范围，不能包含用户的无关改动。
- 以仓库 `docs/contributing.md` 的“GIT提交规范”为准，提交标题使用 `<标记>: <中文概要> [TAPD/Issue 关键字]`。
- 所有手工提交的标题概要和正文必须使用中文；规范标记、代码标识符和平台关键字保留原文。
- 允许的标记为：`feature` / `feat`、`bug` / `fix` / `bugfix`、`refactor` / `perf`、`test`、`docs`、`info`、`format`、`merge`、`depend`、`chore`、`del`。
- 关联 TAPD 时将 `--story=<id>` 或 `--bug=<id>` 放在标题末尾，例如：`fix: 修复租户切换后菜单未刷新 --bug=123456789`。
- 一个提交只选择最符合主要改动性质的标记；提交后用 `git log -1 --pretty=format:'%H%n%s'` 核对中文概要和关联关键字。

## 完成标准

- 实际 diff 仅包含任务相关改动，没有本地配置、敏感信息、调试代码或大范围无关格式化。
- 新增行为覆盖主路径、失败路径和关键边界；缺少自动化测试能力时明确说明验证方式。
- 用户可见文案、接口类型、路由权限和共享状态已按改动同步。
- `git diff --check` 通过，并按风险完成 lint、i18n 检查或构建；未执行项需说明原因。

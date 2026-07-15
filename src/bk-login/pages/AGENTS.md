# AGENTS.md

## 适用范围

本文件适用于 `src/bk-login/pages/` 下的统一登录前端。用户在当前任务中的明确要求优先于本文件；若说明与源码或配置不一致，以当前 `package.json`、构建配置和实际代码为准。

开始工作前先执行 `git status --short`，识别并保留用户已有改动。只修改完成任务所必需的文件，不顺手格式化或重构无关代码。

## 项目概览

- 技术栈：Vue 3、TypeScript、Composition API、Pinia、Vue Router、Vue I18n、BKUI Vue、CSS。
- 构建工具：`@blueking/cli-service-webpack`，入口为 `src/main.ts`。
- `src/views/`：登录、协议和用户页面；`src/components/`：共享组件；`src/composables/`：共享组合逻辑。
- `src/http/`：接口、类型和请求拦截；`src/store/`：Pinia 状态；`src/router/`：路由配置。
- `src/language/zh.json` 与 `src/language/en.json`：中英文文案；`src/css/`：全局样式。
- `static/`：静态资源；`paas-server/`、`mock-server/`、`bin/`：本地服务和构建脚本。

## 开发约定

- 优先延续相邻代码的组件组织、命名、类型和错误处理方式，不引入平行实现。
- 新增或修改的代码注释使用中文，只解释业务原因、边界条件和非显而易见的取舍。
- 组件优先使用 Composition API 和 TypeScript；保持职责单一，复杂逻辑抽到现有 composable 或工具模块。
- 优先复用 `bkui-vue`、仓库已有组件和样式变量，不重复实现通用控件，不通过全局样式覆盖修复局部问题。
- 为接口入参、返回值、组件 props、emits 和共享状态提供明确类型；避免新增 `any`，确实无法避免时缩小范围并用中文注释说明原因。
- 用户可见文本必须通过 Vue I18n 获取，并同步维护 `zh.json` 与 `en.json`；不要在登录提示、协议、通知或异常分支中新增硬编码文案。
- 接口调用统一放在 `src/http/` 现有分层中，同时维护对应类型；跨页面共享状态优先使用现有 Pinia store。
- 登录链路属于高风险区域。修改认证、回调、重定向、用户信息或请求拦截时，必须检查未登录、登录失败、回调参数缺失、刷新、直达 URL 和退出登录场景。
- 不绕过认证校验、CSRF、重定向白名单或敏感字段脱敏来完成需求；不得在日志或页面中暴露密码、票据、Token、Cookie 和完整回调参数。
- 不直接渲染不可信 HTML；协议或自定义内容确需使用 HTML 时沿用项目已有 `vue-dompurify-html` 方案并验证 XSS 边界。
- 表单和异步操作需处理重复提交、加载态、失败提示及组件卸载后的状态更新。
- 样式修改至少检查常见窗口宽度、长文本、空状态及中英文布局，并确认登录页关键操作在不同尺寸下可见可用。

## 环境与依赖

- 使用 npm 管理依赖，不混用 Yarn 或 pnpm。
- 当前 `package-lock.json` 被子项目 `.gitignore` 忽略；不要擅自提交锁文件或调整忽略规则。依赖变更至少更新 `package.json`，并在交付中说明验证环境。
- 本地环境配置不得包含或提交 Token、Cookie、真实账号、内部地址、生产密钥和生产数据。
- 不提交 `node_modules/`、`dist/`、缓存、日志、`.DS_Store` 或编辑器临时文件。
- 不为消除版本警告而批量升级依赖；新增依赖前先确认现有工具或依赖无法满足需求，并评估登录页产物体积和兼容性。

## 常用命令

在 `src/bk-login/pages/` 目录执行：

```bash
npm run dev
npx eslint --ext .js,.vue,.ts ./src
npx stylelint "**/*.{html,vue,css,sass,scss,less}"
npm run build
```

- 优先运行与改动最相关的检查；涉及认证流程、路由、构建配置或依赖时再运行完整构建和关键登录流程验证。
- `npm run lint:fix` 和 `npm run lint:style` 都会修改文件，不能当作只读检查命令；执行后必须立即检查 diff。
- 项目未定义单元测试和只读 lint 脚本，不要声称测试已通过；使用上面的 `npx` 命令进行只读检查，并说明手工验证范围。
- 仅修改 `AGENTS.md` 等规则文档时，无需运行完整业务构建，但至少执行 `git diff --check` 并核对文档中的命令和路径。

## Git 提交规范

- 只有用户明确要求时才创建 commit、push 或 PR；提交前必须核对 staged 范围，不能包含用户的无关改动。
- 以仓库 `docs/contributing.md` 的“GIT提交规范”为准，提交标题使用 `<标记>: <中文概要> [TAPD/Issue 关键字]`。
- 所有手工提交的标题概要和正文必须使用中文；规范标记、代码标识符和平台关键字保留原文。
- 允许的标记为：`feature` / `feat`、`bug` / `fix` / `bugfix`、`refactor` / `perf`、`test`、`docs`、`info`、`format`、`merge`、`depend`、`chore`、`del`。
- 关联 TAPD 时将 `--story=<id>` 或 `--bug=<id>` 放在标题末尾，例如：`fix: 修复登录回调失败后未显示提示 --bug=123456789`。
- 一个提交只选择最符合主要改动性质的标记；提交后用 `git log -1 --pretty=format:'%H%n%s'` 核对中文概要和关联关键字。

## 完成标准

- 实际 diff 仅包含任务相关改动，没有本地配置、敏感信息、调试代码、构建产物或大范围无关格式化。
- 登录成功与失败、重定向、退出登录、多语言和异常分支已按改动风险验证。
- 用户可见文案、接口类型、路由和共享状态已按改动同步。
- `git diff --check` 通过，并按风险完成 ESLint、Stylelint 或构建；未执行项需说明原因。

# 熵管理（Entropy Management）

> 目标：让系统"保持整洁"——通过自动化机制控制系统熵增速度，确保长期可维护。

## 1. 文档园艺机制

### 1.1 自动一致性检测

| 检测项 | 频率 | 方式 |
|-------|------|------|
| 文档引用的文件路径是否存在 | 每次 PR / 巡检 | harness-engineering 文档巡检 |
| `architectural-constraints.md` 与 import-linter 契约是否一致 | 分层变更时 | 人工核查 + 巡检 |
| `tooling.md` Skill 清单与 `$SKILL_ROOT/*/SKILL.md` 是否一致 | Skill 增删时 | 巡检 |
| 前端文案 `zh.json` 与 `en.json` 是否同步 | 每次前端 PR | `npm run i18n` + 评审 |
| standards 预设是否与治理仓预设漂移 | 定向巡检 | 与 `assets/standards/` 比对 |

### 1.2 园艺流程

1. 检测到不一致 → 记录差异（触发词："文档巡检" / "检查文档一致性"）。
2. 简单不一致（路径变更、清单遗漏）→ Agent 直接修复。
3. 复杂不一致（分层逻辑、契约变更）→ 提示责任人确认后修复。
4. 修复后复核关联组件（如改分层须同时看架构约束与工具能力）。

## 2. 架构违规检测

### 2.1 检测策略

| 检测类型 | 触发时机 | 工具 | 阻断级别 |
|---------|---------|------|---------|
| 分层 / 独立性违规 | pre-commit / CI | import-linter | 阻断合并 |
| 代码风格违规 | pre-commit / CI | ruff（format + lint） | 阻断合并 |
| 类型错误 | pre-commit / CI | mypy | 阻断合并 |
| 圈复杂度超限 | pre-commit | ruff mccabe（max-complexity=10） | 阻断合并 |
| 安全红线 | Code Review | `docs/standards/security-bk-redlines.md` | 阻断合并 |

> pre-commit 按目录分别指向 `src/bk-user`、`src/bk-login` 的 `pyproject.toml`，执行 ruff / mypy / import-linter。

### 2.2 违规处理流程

- **阻断级别**：PR 无法合并，必须先修复。
- **警告级别**：允许合并，但记入技术债清单。
- **报告级别**：仅记录，定期批量处理。

## 3. 技术债追踪

### 3.1 追踪机制

| 债务类型 | 识别方式 | 记录位置 | 清理策略 |
|---------|---------|---------|---------|
| import-linter `ignore_imports` 例外 | 契约文件 | 契约注释 | 每迭代复审是否可消除 |
| 遗留 v2 配置（根 `pyproject.toml` 的 black/isort/flake8） | 人工 | 本文档 | 待旧结构完全下线后清理 |
| 空占位（如 `integration_test/scripts/`） | 人工 | 本文档 | 补齐或移除 |
| 过时文档 | 文档巡检 | 巡检报告 | 发现即修复 |
| TODO/FIXME | 代码扫描（ruff） | 代码内 | 每迭代 Review |

### 3.2 技术债预算

- 新增 import-linter 例外须在 PR 说明中给出原因与清理计划。
- 每迭代至少复审并尝试消除 1 条历史例外或遗留配置。<!-- TODO: 待确认——具体预算阈值由团队约定 -->

## 4. 熵增度量

| 指标 | 计算方式 | 阈值 | 超标动作 |
|------|---------|------|---------|
| 分层违规数 | 每周新增 import-linter BROKEN 数 | 0 | CI 阻断，禁止合并 |
| 文档一致性率 | 一致文档数 / 总文档数 | ≥ 95% | 触发集中巡检修复 |
| ignore_imports 数量 | 契约中例外条目数 | 不增长 | 复审并清理 |
<!-- TODO: 待确认——阈值可根据团队实际调整 -->

## 检查清单

- [ ] import-linter / ruff / mypy 已接入 pre-commit 与 CI
- [ ] 文档园艺（巡检）机制可通过 harness-engineering 触发
- [ ] 技术债（例外条目、遗留配置、空占位）已登记
- [ ] 熵增度量指标与阈值已定义

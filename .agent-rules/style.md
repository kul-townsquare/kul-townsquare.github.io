# 代码规范、工作流与质量门禁

## 代码规范

### JavaScript / Vue（产品主代码）

- **ES2015+**，Vue 2 SFC：`<template>` / `<script>` / `<style lang="scss" scoped>`
- 遵循既有 ESLint + Prettier 配置（`.eslintrc.js`）：
  - `plugin:vue/essential` + `eslint:recommended` + `@vue/prettier`
  - `no-console` / `no-debugger` 在 production 构建中警告
  - 不启用 `vue/multi-word-component-names`（历史原因，已关）
- **命名**：
  - 变量 / 函数：`camelCase`
  - Vue 组件文件：`PascalCase.vue`
  - Vuex module：`camelCase.js`；action `camelCase`；mutation `SCREAMING_SNAKE_CASE`
  - 常量：`UPPER_SNAKE_CASE`
  - SCSS class：`kebab-case`
- **模块**：ES Modules `import / export`
- **JSDoc**：仅在"意图非平凡"时写（外部契约、复杂逻辑、反直觉的工作流）；不写复读代码的注释
- **异步**：统一 `async / await`，不要混 Promise chain

### SCSS

- 全局变量集中在 `src/vars.scss`
- 响应式 breakpoint 用 `src/media.scss` 中的变量
- 组件样式默认 `scoped`；需穿透时用 `::v-deep`
- 避免 > 3 层选择器嵌套

### Python 维护脚本（根目录 `*.py`）

- Python 3.8+ 即可；这些是**一次性数据维护脚本**，不跑生产
- 简洁优先，不强制 type hints 或 Google docstring
- 直接用系统 `python3` 调用（`python3 add_edition_and_roles.py`），无需虚拟环境
- 新脚本沿用同一位置（根目录）与同一风格（见现有 6 个脚本）

## Git 工作流（严格遵守 `CONTRIBUTING.md`）

### 分支策略

- `main` —— **线上生产分支**（直接对应 `clocktower.online`）
- `develop` —— 下次发版分支；功能分支都 PR 到 `develop`
- `feat/<描述>` —— 新功能
- `fix/<描述>` —— Bug 修复
- `refactor/<描述>` / `docs/<描述>` / `chore/<描述>` —— 重构 / 文档 / 杂项
- 只有 `develop` → `main` 的 release PR 能合并到 `main`

**禁止**直接向 `main` 推代码或提交。

### Commit 规范

- **格式**：`<type>: <简短描述>`
- **type**：`feat` / `fix` / `refactor` / `docs` / `style` / `test` / `chore` / `deploy`
- **语言**：英文
- 小步提交 OK（PR 合并时 GitHub 会 squash）
- **禁止** `--no-verify` 跳过 hooks

### PR 规范

- **PR 目标**：**永远是 `develop`**，不是 `main`（release PR 除外）
- **PR 标题**：
  - 修 bug 时引用 issue：`fix custom script upload (fix #1234)`
  - 语言英文（与上游一致）
- **PR 前必须完成**：
  - [ ] 更新 `CHANGELOG.md`（CONTRIBUTING.md 强制要求）
  - [ ] `npm run lint-ci` 通过
  - [ ] `npm run serve` 本地浏览器实测改动生效
  - [ ] 不破坏任何「用户契约」（见 `core.md`）
- **禁止**提交：
  - `dist/` 目录
  - `node_modules/`
  - 超大二进制

## 语言规范

| 场景 | 语言 |
|---|---|
| Agent 与用户交互 | 中文 |
| 代码注释 / JSDoc | 英文 |
| Commit message | 英文 |
| PR 标题 | 英文（与上游/开源习惯一致） |
| PR 描述 | 中英文均可，引用 issue 用 `#NNNN` |
| `README.md` / `CHANGELOG.md` / `CONTRIBUTING.md` | 英文为主（与上游保持一致） |
| 规划文档（`.planning/*.md`） | 中文 |
| UI 文案（`src/` 内） | 英文为主 + 中文本地化 |

## 实施流程

1. **Understand** —— 先读相邻实现，至少找 1 处相似模式作为参考
2. **Plan**（Level 2 / 3 时）—— 简要说明或规划文档，等用户确认
3. **Implement** —— 最小改动通过验证
4. **Verify** —— lint + 浏览器实测（UI 改动不能只看 diff）
5. **Document** —— 更新 `CHANGELOG.md` + 必要时更新 README / JSDoc
6. **Commit** —— 英文 message 说 why，引用 issue 或规划文档

## 质量门禁

完成前必须满足：

1. **Lint** —— `npm run lint-ci` 通过（`--no-fix --max-warnings=0`）
2. **浏览器验证** —— `npm run serve` 并在浏览器实测改动生效；**UI 改动未经浏览器实测不得声称完成**（类型检查与 lint 只能证明代码正确，不能证明功能正确）
3. **用户契约保留** —— 未破坏 `core.md` 列出的 6 类契约
4. **CHANGELOG** —— 除纯内部重构 / 文档外，改动必须写入 `CHANGELOG.md`
5. **回归意识** —— 改动应考虑对既有玩家与既有自定义剧本的影响
6. **Codex 代码审查通过** —— 属于下节触发范围的改动

## 代码审查（Codex Review Gate）

本项目使用 OpenAI Codex 作为 AI 代码审查工具。各 Agent 的具体调用方式见各自的指令文件（`CLAUDE.md` / `.cursor/rules/` 等）。

### 何时触发

- 完成一个功能分支或逻辑完整的代码块后（对应实施流程第 4–5 步之间）
- Level 2 / Level 3 改动完成后（见 `approval.md`）
- 修改核心代码后：
  - `src/store/` Vuex 结构
  - `server/` WebSocket 协议
  - `src/roles.json` / `editions.json` 等数据 schema
  - `vue.config.js` / 构建配置
  - 任何影响用户契约的改动

### 审查重点（针对本项目）

- **正确性与 bug** —— 尤其是 session state 同步、WebSocket 消息处理、Vuex mutation/action 副作用
- **用户契约兼容性** —— `roles.json` 字段、URL、localStorage、WebSocket 消息是否破坏向后兼容
- **ESLint 规范与项目一致性** —— 命名、模块结构、Vue 2 SFC 惯例
- **性能** —— bundle size、首屏关键路径、不必要的响应式开销
- **错误处理** —— 是否有裸 `catch`、是否吞异常、日志是否带定位上下文

### 豁免（不必走 Codex）

- Level 1 改动（单文件 UI / bug / 文案 / 注释 / patch 依赖）
- 纯 `README` / `CHANGELOG` / `docs` 更新
- 根目录 `*.py` 维护脚本
- 明显的非功能性改动（clean up、变量改名）

## 用户契约优先

当新需求与"用户契约"冲突（如改 `roles.json` schema 能简化代码但会破坏老剧本）：

1. **默认选兼容**：保留老字段，新字段叠加
2. 破坏性改动必须在 `CHANGELOG.md` 以 `BREAKING:` 前缀高亮
3. 提供迁移路径或 fallback，而非直接断链

## 技术决策排序

评估顺序（冲突时按此优先级取舍）：

1. **用户影响** —— 不破坏现有使用方式
2. **可验证性** —— 能用浏览器或单测验证
3. **可读性** —— 与项目既有代码风格一致
4. **简洁性** —— 最少必要的改动
5. **可逆性** —— 改错容易回滚

## 卡住处理

同一问题 3 次尝试失败后停止硬改：

1. 记录已试方案、报错、失败原因（写到 `.cursor/findings.md`）
2. 查看项目内或上游 `bra1n/townsquare` 是否有类似实现
3. 拆成更小、更可验证的步骤，和用户讨论后再走

## 错误处理

- **快速失败，提供可定位上下文**：WebSocket / socket 错误要带 session ID / 玩家 ID / 消息类型
- 不吞异常，不裸 `catch`（无日志的 catch 视为 bug）
- UI 层错误告知用户要克制（非阻塞提示 / 可恢复），避免弹框恐慌
- 调试用 `console.log` 提交前清理；必要的生产日志用 `console.warn` / `console.error`

## 性能与包大小

- 新增生产依赖前评估 bundle 影响（`npm run build` 观察产物大小）
- 新增图片 / 音频资源必须压缩；身份图标优先 SVG，其次压缩后的 PNG
- 避免在 Vuex state 里放大对象或图片二进制

## 权限约定（Agent 操作）

**读操作默认允许**。以下操作必须先征得用户确认：

- `npm install <new-package>` / `npm update`（影响 lock 文件与 bundle）
- `git push`（尤其是任何推到 `main` 的行为）
- 批量改写（≥ 5 个文件的 sed / replace）
- 删除文件
- 修改 `vue.config.js` / CI 配置 / `package.json` `scripts` 段
- 任何 Level 3 改动（见 `approval.md`）

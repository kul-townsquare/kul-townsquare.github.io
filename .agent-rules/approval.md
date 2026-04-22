# 任务审批规则（所有 Agent 必须遵守）

## 核心原则：规划重量与 blast radius 成正比

改动的影响面决定审批门槛。Agent 不得对所有改动一刀切地走重流程，也不得对高风险改动绕过规划。

## 三档分级

### Level 1 — 直接开工
以下情形 Agent 可直接动手，无需事先说明或规划：

- 单文件 UI / 样式微调（不改组件结构）
- Bug 修复，且影响局限于单个组件或函数
- 文案、i18n 文本更新
- 注释 / JSDoc 补充
- 依赖 patch 级升级（`x.y.Z`）
- `README.md` / `CHANGELOG.md` / `docs/` 文档改动
- 清理死代码、未使用 import

### Level 2 — 简要确认
开工前用 1–2 句话告知用户计划并等待确认（`好` / `确认` / `go` 等），不需要创建规划文件：

- 新增单个 Vue 组件
- 新增 Vuex module 或 action / mutation
- 新增单个身份 / edition / fabled 数据条目
- 新增一组内聚的工具函数或 mixin
- 依赖 minor / major 升级
- 根目录维护脚本（`*.py`）改动
- `server/` 内非协议性改动（日志、metrics、错误处理）

### Level 3 — 必须规划文档
在 `.planning/` 创建规划文件并等待用户明确批准，才能写代码：

- **任何用户契约变更**（见 `core.md` 的「用户契约」节），包括：
  - `src/roles.json` 字段 schema
  - 自定义 script JSON 的 `_meta` 约定
  - 分享 URL 格式
  - `localStorage` 键名或值结构
  - WebSocket 消息类型或字段
- `server/` 的协议层改动
- Vuex store 顶层结构、全局事件流、路由改动
- `vue.config.js` / CI / GitHub Pages 部署配置变更
- 涉及 ≥ 3 个 `src/` 文件联动的重构
- 任何可能影响线上 `clocktower.online` 用户体验的改动（性能回归、首屏变化、关键交互改动）
- 新增生产依赖（影响 bundle size）

> 判断不清属于哪一档时，**上靠一档**，宁愿多问一句不要少走一步。

## 规划文件规范

**位置**：统一放在 `.planning/` 目录（不在 `.cursor/` 或根目录）

**命名**：`.planning/{YYYYMMDD}_{task_name}.md`

**格式**：

```markdown
## 任务：[具体任务名]

**背景**：[为什么做、要解决的用户/开发问题]
**影响范围**：[会修改或创建的文件列表 + 受影响的用户契约]
**前置条件**：[依赖哪些已完成的工作]
**风险**：[可能破坏的东西，以及回滚方案]

### Stage 1: [阶段名]
- **目标**：[具体交付物]
- **成功标准**：[可验证的结果 — 建议包含浏览器实测步骤]
- **状态**：Not Started

### Stage 2: [阶段名]
...

**待确认事项**：[需要用户决策的问题，逐条列出]
```

## 批准信号

用户明确给出以下信号才可开始执行：

- 「好」「确认」「开始」「go」「ok」「yes」「proceed」「没问题」

收到模糊回应时（如「嗯」「看看」）**必须追问**，不得默认批准。

## 规划文件生命周期

- 只追加更新，不删除历史规划
- 执行中更新 Stage 状态（`Not Started` → `In Progress` → `Complete`）
- 完成后追加 `## 完成记录`：完成时间、实际结果、偏差说明、CHANGELOG 对应条目
- 历史规划文档永久保留

## 会话恢复

会话中断或重启后：
1. 先读 `.cursor/task_plan.md`、`.cursor/progress.md`、`.cursor/findings.md` 了解当前执行状态
2. 再读 `.planning/` 最近的规划文件了解整体规划

## 执行中进度跟踪

会话中使用 `.cursor/` 下的文件记录：

- `task_plan.md`：任务拆解与状态（`planned` → `in_progress` → `done`）
- `progress.md`：按日期追加会话进展
- `findings.md`：关键发现、技术结论、踩坑记录

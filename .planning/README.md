# .planning/ — 任务规划文件目录

所有 AI Agent（Claude Code / Cursor / Codex）在执行 **Level 3 改动**（见 `.agent-rules/approval.md`）前，必须在本目录创建规划文件并等待用户明确批准。

## 何时需要规划文件

属于 Level 3 的改动：

- 用户契约变更（`roles.json` schema、`_meta`、分享 URL、localStorage、WebSocket 消息）
- `server/` 协议层改动
- Vuex store 顶层结构、全局事件、路由
- `vue.config.js` / CI / 部署配置
- ≥ 3 个 `src/` 文件联动的重构
- 可能影响 `clocktower.online` 线上用户体验的改动
- 新增生产依赖

Level 1（单文件 UI/bug/文案）与 Level 2（单组件/单 module）改动**不需要**规划文件。

## 命名规范

```
{YYYYMMDD}_{task_name}.md
```

示例：
- `20260501_custom_script_meta_v2.md`
- `20260512_live_session_reconnect.md`
- `20260603_roles_json_add_sect.md`

## 文件格式模板

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
- **目标**：...
- **成功标准**：...
- **状态**：Not Started

**待确认事项**：
- [ ] 问题一
- [ ] 问题二
```

## 生命周期

1. Agent 创建规划文件 → 等待用户批准
2. 用户给出批准信号（`好` / `确认` / `go` / `ok` / `proceed` / `没问题`）后 → 开始执行，更新各 Stage 状态
3. 完成后追加 `## 完成记录`：完成时间、实际结果、偏差说明、对应 CHANGELOG 条目
4. 历史文件永久保留，不删除（供审计与复盘）

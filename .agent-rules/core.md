# 项目核心规则

## 项目定位

**项目名称**：`kul-townsquare.github.io`

**产品**：《染：钟楼谜团》（Blood on the Clocktower，BotC）说书人辅助程序 —— 一款面向桌游线下聚会 + 线上游戏的城镇广场（Town Square）与 Grimoire 工具。

**核心用户场景**：
1. **说书人（Storyteller, ST）** 打开 Grimoire 管理本局游戏状态（身份、提醒、夜晚行动）
2. **玩家** 用各自的设备进入对应房间（Live Session）
3. **说书人分配身份**，玩家在自己的设备上查看自己的身份与夜间信息
4. 支持投票、提名、死亡 / 中毒 / 醉酒标记、夜晚行动顺序等游戏流程辅助
5. 支持官方三版本 + 旅行者 + 传奇角色 + 自定义剧本（JSON）

**项目性质**：
- 开源社区产品（GPL-3.0），fork 自 `bra1n/townsquare`
- 已部署到 GitHub Pages，生产环境直面用户
- 主要用户群：中文 BotC 游戏圈的说书人与玩家
- 本 fork 的差异化方向：中文本地化、中文社区剧本、中文身份图标/资源

**参考资料**：
- 游戏中文百科：`https://clocktower-wiki.gstonegames.com/`（需查阅身份机制 / 中文译名时参考；本地索引见 `.cursor/memory/reference_botc_wiki.md`）
- 上游项目：`https://github.com/bra1n/townsquare`
- 线上英文版：`https://clocktower.online`
- 官方 Script Tool：`https://script.bloodontheclocktower.com/`

## 技术栈

| 层 | 技术 |
|---|---|
| 前端框架 | Vue 2.7（SFC）+ Vuex 3 |
| 样式 | SCSS（`sass` + `sass-loader`） |
| 构建 | Vue CLI 5（webpack 底层） |
| Lint / Format | ESLint + Prettier（`@vue/eslint-config-prettier`） |
| 后端（Live Session） | Node.js + `ws` WebSocket + `prom-client` 指标 |
| 图标 | FontAwesome |
| 维护脚本 | Python 3（根目录 `.py` 脚本，用于批量处理 `roles.json` 等数据） |
| 部署 | GitHub Pages（`main` 分支） |

**Node**：建议 18+（参见 CHANGELOG `2.16.2` 的升级记录）。开发环境需 Chrome 浏览器验证。

## 目录规范（对应项目实际结构）

```
src/                    # Vue 产品代码（ES2015）
├── App.vue             # 根组件
├── main.js             # 入口
├── components/         # 内部组件
│   └── modals/         # 模态框单独子目录
├── store/              # Vuex
│   └── modules/        # 带命名空间的 Vuex 模块
├── assets/             # 图形资源
│   ├── editions/       # 版本 logo
│   ├── icons/          # 身份 token 图标（PNG，透明背景）
│   ├── fonts/          # webfont
│   └── sounds/         # 音效
├── roles.json          # ⚠ 用户契约：身份数据
├── editions.json       # 版本数据
├── fabled.json         # 传奇角色数据
├── game.json           # 游戏规则数据
├── hatred.json         # 配对/仇恨数据
├── vars.scss           # SCSS 变量
└── media.scss          # 响应式断点

server/                 # Live Session WebSocket 后端
public/                 # 静态资源（不经构建）
剧本JSON/                # 预制中文剧本 JSON（社区资源）
根目录 *.py              # 一次性数据维护脚本
.planning/              # 规划文档（按任务命名）
.cursor/                # Agent 会话态 + 记忆（memory/、task_plan.md 等）
.agent-rules/           # 规则 canonical 源（编辑后需运行 sync_agent_rules.py）
dist/                   # ⚠ 构建产物，不进 Git
```

**禁止**：
- 提交 `dist/`（CONTRIBUTING.md 硬性规定）
- 提交 > 5MB 的二进制（图片应预先压缩或改用外链；根目录已有的历史 PNG 不在此限）
- 在 `src/` 之外写产品代码（`src/` 内是唯一的 Vue 源树）

**允许**：
- 根目录 `.py` 维护脚本（既有约定，`add_edition_and_roles.py` 等 6 个脚本就是这样组织的）；新增时沿用同一位置

## 用户契约（Backward Compatibility Contracts）

以下是**不可随意破坏**的对外契约，**任何改动都要走 Level 3 规划 + CHANGELOG 显式标注**：

1. **`src/roles.json` 字段 schema**
   —— 社区自定义脚本依赖这个 schema（`id` / `name` / `team` / `ability` / `firstNight` / `reminders` / …）
2. **自定义 script JSON 的 `_meta` 对象**
   —— 见 README 说明的 `id: "_meta"` / `name` / `author` / `logo`
3. **分享 URL 格式**
   —— 用户可能已经分享了链接给他人；query/hash 结构视同 API
4. **`localStorage` 键名与值结构**
   —— 影响老用户的本地存档（设置、自定义剧本、音量等）
5. **WebSocket 消息类型与字段**（`server/` ↔ `src/store/socket.js` 等）
   —— 新旧客户端需互通；不同版本玩家可能在同一房间
6. **身份 ID（`id` 字段）**
   —— 引用该 ID 的剧本会因为改名/删除而失效；官方身份的 ID 必须保持稳定

违反上述契约的改动默认拒绝；确需改动时：
- 优先选 **叠加**（新字段共存，老字段保留）
- 必要时提供 **迁移**（localStorage 自动升级、fallback 读取旧 URL）
- CHANGELOG 以 `BREAKING:` 前缀高亮

## Claude Code 记忆存储规范

Claude Code 的持久化记忆必须存在项目目录内，不用全局路径：

- **记忆根目录**：`.cursor/memory/`
- **索引文件**：`.cursor/memory/MEMORY.md`（只放链接，不写内容）
- **记忆文件命名**：`{type}_{topic}.md`，如 `project_user_contract.md`、`reference_botc_wiki.md`
- **禁止** 使用 `~/.claude/` 或任何项目外路径

每个记忆文件使用如下 frontmatter：

```markdown
---
name: 记忆名称
description: 一句话描述（用于判断未来会话相关性）
type: user | feedback | project | reference
---

内容
```

## 外部资源查阅策略

- 访问 `clocktower-wiki.gstonegames.com` 等外部文档时，**首次查询后在 `.cursor/memory/` 建立索引/摘要**，避免在后续会话重复访问
- 索引记忆文件命名：`reference_<资源名>.md`
- 只记录对项目有用的条目（身份中文名、机制描述、规则细节），不抄全文

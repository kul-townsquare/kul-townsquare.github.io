# 会话进展日志

按日期倒序。最新在上。

---

## 2026-04-23

### 上下文
用户（BotC 玩家，比利时）是 `kul-townsquare.github.io` 的维护者，该仓库 fork 自 `bra1n/townsquare`，生产部署在 GitHub Pages + 上游 `wss://live.clocktower.online:8080/`。希望把 WSS 后端自建到自己的 fnOS NAS。

### 本次会话完成的工作

**仓库基础设施（上半段会话）**
- 初始化 AI 规则模板（`.agent-rules/` canonical source + `sync_agent_rules.py` 同步脚本）
- 重写为产品开发导向（删除原模板的 Python/科研项目假设），引入**三档审批制**（Level 1 直接开工 / Level 2 简要确认 / Level 3 规划文档）
- 6 个用户契约显式枚举：`roles.json` schema、自定义 script `_meta`、分享 URL、localStorage、WebSocket 消息、role ID
- 规则同步到 `CLAUDE.md` / `AGENTS.md` / `.cursor/rules/00_synced.mdc`

**工具与数据质量**
- 新增 `validate_scripts.py` —— 对 `剧本JSON/` 下 495 个剧本做 schema 校验
- 扫出 15 个真错误（BOM × 3、空 JSON × 1、重复 ID × 6、`traveller` 拼写 × 3、`setup` 错值 × 2）
- Codex 审过一轮修复

**迁移 Stage 1–2**
- Stage 1：`cloudflare/cloudflared` 镜像拉取 + 冒烟测试隧道。命中 BRU 边缘（布鲁塞尔 POP），延迟理想
- Stage 2：Dockerize `server/index.js`
  - 新增 `server/Dockerfile`（pin digest `node:22-alpine@sha256:8ea2348b...`）
  - 新增 `server/package.json`（独立后端依赖 `ws` + `prom-client`）
  - 新增 `server/package-lock.json`（`npm ci` 可重现构建）
  - 新增 `server/.dockerignore`
  - 新增 `docker-compose.yml`（read_only / cap_drop ALL / no-new-privileges / 256 MiB / 0.5 CPU / 100 pids / tmpfs 16m 带 noexec,nosuid,nodev）
  - 端口绑 `127.0.0.1:8081`（LAN 不可达已实测）
  - 容器 `healthy`、非 root uid 1000
  - Codex 审过一轮，修复 4 个 should-fix + 2 个 nice-to-have（见 commit `90ea25e`）
- `.gitignore` 加 `.env`, `.env.*`, `*.key`（补 Stage 2 漏掉的安全项）

**Stage 3 的外部准备（今天这段）**
- 讨论了 cloudflared 部署方式，用户选择 `sudo cloudflared service install <TOKEN>` 在 host 以 systemd 安装，而非 Docker sidecar
- 威胁模型评估：可接受（cloudflared 无入站端口，用户可信，边际隔离价值不大）
- 已做安全补强 B（自动更新 + CF 账号 2FA），未做补强 A（token 文件化）
- 域名决策：用户不想付费，选 `.eu.org` 免费子域名路径（放弃 `.xyz` 付费方案）
- 用户注册 eu.org 账号 `ZN196-FREE`，域名 `kul-botc.eu.org` 申请表单填写
- 在 CF 侧 `Add a site` 加入 `kul-botc.eu.org`，CF 分配 NS pair：`oaklyn.ns.cloudflare.com` + `piotr.ns.cloudflare.com`
- eu.org 表单填 NS pair，选最严校验模式（`noms de serveurs + SOA + NS`），已提交

### Commit 列表（按时间）

```
b747450 chore: initialize AI coding agent rules for vibe-coding workflow
e99dbc4 feat: add validate_scripts.py guardrail for BotC script JSONs
14f8926 style: strip trailing whitespace in EditionModal.vue
a3f972c fix: address Codex review findings on validate_scripts.py
5b03f03 docs(planning): write Level-3 self-host plan with Codex review fixes
33101c8 feat(server): dockerize WSS backend with hardened compose (Stage 2)
90ea25e fix(server): address Codex Stage 2 review findings + .gitignore safety
```

所有 commit 在 `vibe-dev` 分支，**均未推送**。

### 当前运行状态（NAS 侧）

- `docker compose ps` 显示 `kul-townsquare-wss` 容器 `healthy`，6+ 小时 up
- `cloudflared` systemd 服务 `active running`，已自动更新启用
- 前端仍连上游 `wss://live.clocktower.online:8080/`（未改代码），生产服务零影响
- `.env` **不存在**于仓库根（按用户说法 token 通过 cloudflared 官方安装脚本直接进了 systemd unit，不需要 `.env`）

### 等待中的外部事件

**eu.org 人工审批 `kul-botc.eu.org`** —— 1 周到数月不等。期间无需任何操作。

### 用户个人设置备忘

- 使用 Tailscale 个人访问 NAS（不在本项目范围内，保持不动）
- Gmail 作为注册邮箱（eu.org 邮件可能进垃圾箱，需排查）
- 全部 NAS 本地用户可信
- 原则：不推 main；commit 不带 co-author；规划/对话用中文，代码/commit 用英文

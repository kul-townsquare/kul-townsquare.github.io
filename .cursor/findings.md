# 关键技术发现与踩坑记录

按主题分类。跨多会话持久保留。

## BotC 项目特有

### 中文社区剧本不用官方 Script Tool
- 495 个 `剧本JSON/` 里 96% 条目嵌入完整 `ability` 文本，仅 0.3% 用 `{id}` 引用
- 因此**官方 Script Tool 兼容性不是 P0 问题**（早期误判为关键 bug，后证伪）
- 详见 `.cursor/memory/project_script_format.md`

### `server/index.js` NODE_ENV 分支行为
- `NODE_ENV=development`：WebSocket 直接 `new Server({ port: 8081 })`，无 HTTPS server，metrics 端点**不暴露**（对我们有利）
- `NODE_ENV=production`：`server.listen(8080)` 启动 HTTPS server，需 `cert.pem` / `key.pem`，metrics 端点在 8080 每个请求路径都返回
- CF Tunnel 部署时选 **`NODE_ENV=development`** 让 CF 做 TLS termination，省证书管理同时自动消除 metrics 暴露

### `server/index.js:25-29` origin 白名单正则
- 现状：`/^https?:\/\/([^.]+\.github\.io|localhost|clocktower\.online|eddbra1nprivatetownsquare\.xyz)/i`
- 两个坑：(1) 前缀匹配而非完整匹配，`https://clocktower.online.evil.com` 会过；(2) `clocktower\.online` 任意子域包含 `live.` 也匹配
- Stage 4 要加新前端域名时顺手修成 `^https?://.../...(:port)?/?$` 尾锚定

### URL path 格式是两段 `/<channel>/<playerId-or-host>`
- `server/index.js:107-110` 用 `req.url.split("/")` 解析 `[playerId, channel]` 从尾部弹
- CF Tunnel WAF 正则要匹配**两段**，不是一段
- 错误的 `^/[a-zA-Z0-9-]+$` 会误杀所有正常玩家握手（Codex 审查捕获）

### player 可自选座位
- 用户披露：玩家端可以发消息指定"我坐 N 号"，服务端信任
- 意味着 session ID 的**熵**是事实上的唯一防破门机制
- 现有实现的 session ID 熵未审计；若未来要提升安全可引入 capability token，但属于用户契约 Level 3 变更

## Cloudflare & 隧道

### `*.cfargotunnel.com` 不是公开可访问 URL
- 它只是 CNAME target，不是给浏览器用的域名
- Named Tunnel 要对外访问必须有**自己的 CF zone 域名** + 配置 Public Hostname
- 我早期误以为 CF 分配的 `<uuid>.cfargotunnel.com` 是免费直达 URL —— 错的，已纠正

### Free CF 账号能用到的
- Named Tunnel + Public Hostname（✓）
- 无限带宽 / 流量（✓）
- 基础 WAF Rate Limiting（✓）
- 不能用：per-path / per-channel rate limit（需 Worker 或付费）
- 不能用：DNS Load Balancing（付费 $5/月起）

### `sudo cloudflared service install <TOKEN>` 的行为
- 在 Debian 生成 `/etc/systemd/system/cloudflared.service`
- 以 **root** 运行，token 明文写在 `ExecStart` 命令行里（`ps aux` 可见）
- `--no-autoupdate` 默认打开（建议去掉，让 CF 自动拉新版本）
- 无 `/etc/cloudflared/` 目录（token 不走文件，走命令行）

### cloudflared 的威胁模型比想象中好
- 只做**出站**连接，不 listen 任何端口
- 远程攻击面 = 0（要打它得先打 Cloudflare 边缘）
- "root 运行"这个传统担忧在这个场景下权重大幅降低
- 但仍建议：(1) 自动更新开着，(2) CF 账号 2FA 开着

## eu.org 免费域名

### 审批是**人工**的，队列超长
- 社区志愿者维护，不 SLA
- 2023 Freenom 关停后请求量爆炸
- 常见等待：1 个月到 1 年
- 用户 Gmail 可能收不到激活邮件（`nic.eu.org` SPF/DKIM 不完善，Gmail 容易扔 Spam）
- 排查路径：搜 All Mail 和 Spam、关掉 Filters、换非 Gmail 重注册

### 表单坑
- `Privé (non visible Whois)` 勾上，隐私保护免费（商业注册商收费）
- `Serveurs de noms` 填 CF 分配的 NS pair（要先 `Add site` 拿）
- 不需要 glue records（CF NS 在 `ns.cloudflare.com`，不在被注册域内）
- 校验模式选第 3 档（`noms de serveurs + SOA + NS recommandé`）—— CF 侧一般能过

## 仓库 / 工具链

### `package-lock.json` 随 Node 版本漂
- Node 22 安装会改 lock 的 metadata（registry URL、optionalDependencies 结构等），即使没升级 dep
- 这种"非实质性 lock 漂移"**不应该提交**
- 判断标准：问自己"我是真在升级依赖吗？" 如果不是，`git checkout -- package-lock.json`

### `.claude/settings.local.json` 被 `.gitignore` 忽略
- 正确设计：里面有个人环境特定的路径、工具偏好
- 想共享团队权限基线可用 `.claude/settings.json`（无 `.local.`），本项目当前不需要

### ESLint 历史警告在 `EditionModal.vue`
- 两条 prettier 空格（行 151, 157），早期已清理（commit `14f8926`）
- 现在 `npm run lint-ci` 全绿

### Codex 审查走 MCP 工具不可用
- CLAUDE.md 头部写的 `mcp__codex__codex` 在当前会话环境下未注册
- 实际走 `codex:codex-rescue` 子代理，通过 `codex-companion.mjs` CLI 投递任务
- Codex task 异步执行，用 `node codex-companion.mjs status --all` 查状态、`result <job-id>` 取报告
- 审查质量不错：两轮审都捞出具体的文件:行号级问题

## 项目约束提醒

- 不推任何分支到 `main`
- 绝对不破坏 6 条用户契约（见 `CLAUDE.md` core 节）
- 新增源文件走 Level 2（简要说明后开工），不是每个文件都要 `.planning/`
- 玩家数量少 + 用户可信 + 无付费预算 → 所有方案评估要对齐这三个前提

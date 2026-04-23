## 任务：自建 Live Session WebSocket 后端到 fnOS NAS（经由 Cloudflare Tunnel）

**背景**

现状：前端 `src/store/socket.js:3` 硬编码 `wss://live.clocktower.online:8080/`，所有 Live Session（发身份、投票、提名、状态同步）流量走上游作者 bra1n 的生产服务器。我们想把 WebSocket 后端迁到家里比利时的 fnOS NAS（Debian 12，Docker 28.5.2，15 GiB RAM；已运行 Home Assistant + Tailscale），以便自己掌控。

**用户核心诉求（不可协商的验收标准）**

1. **零玩家侧安装** —— 玩家打开浏览器就能用，不装 Tailscale / VPN / 其他任何客户端
2. **NAS 要有基本防护** —— host 无 iptables / ufw，必须靠 Docker 隔离 + Cloudflare Tunnel "只出不进"抵消
3. **玩家不登录** —— 不启用 Cloudflare Access 邮箱验证；匿名即可进房间
4. **自动回退** —— NAS 挂掉 / 断电时，前端必须能**自动**切回上游 `wss://live.clocktower.online:8080/`，不依赖用户手动重新构建部署
5. **游戏语义**：玩家可自己选座位，会发消息到 server（额外输入信任面；session ID 必须高熵才能抵挡猜测）

**影响范围**

- 新增：NAS 上的 Docker 容器（`kul-townsquare-wss` + `cloudflared` sidecar）
- 新增：Cloudflare 账号 + 域名 + 命名隧道（用户侧一次性配置）
- 修改：`src/store/socket.js`（URL 硬编码 → 环境变量 + 编译期 fallback）—— **用户契约相关**
- 修改：`server/index.js` 的 origin 白名单正则（加新前端域名）—— **用户契约相关**
- 新增：`server/Dockerfile` + 仓库根目录 `docker-compose.yml` + `server/.dockerignore`
- 新增：`.env.example`；`.env`（不进 Git）
- 更新：`server/README.md`（加自建部署章节）
- 更新：`CHANGELOG.md` `Unreleased`

**前置条件**

- 用户回答 Stage 0 的 4 个问题
- 分支 `vibe-dev`（本规划、代码改动都走这条）
- 当前所有改动均未推到任何远端

**风险与回滚总览**

| 风险 | 触发 | 回滚 |
|---|---|---|
| CF Tunnel 中断 | CF 侧故障 / tunnel 凭据失效 | 前端环境变量切回 `wss://live.clocktower.online:8080/`，重新构建部署（~10 min） |
| 新后端 bug | 代码回归 / 容器启动失败 | `docker compose down` + 前端回滚 URL |
| NAS 停电 / 重启 | 物理事件 | Docker `restart: unless-stopped` 自恢复；启动慢时玩家暂时连不上 |
| Tunnel 凭据泄漏 | `.env` 误入 Git / 备份泄漏 | Cloudflare 面板吊销 tunnel，重发凭据 |
| LAN 入侵者扫到 `0.0.0.0:8081` | Docker 误配 host network | compose 里强制 `127.0.0.1:8081:8081` 绑定；Stage 2 验收包括 LAN 不可达检查 |
| 被爬虫 / 恶意扫描打爆 | CF 前的 DoS | CF WAF rate limit；容器 `mem_limit: 256m` 防止内存打穿 |

---

### Stage 0 — 前置问题（用户回答）

**域名**（2026-04-23 用户回答 + 2026-04-23 二次回答）：
> "我不确定能不能用免费的" / "我不希望为我的这个修改付费"

结论：**走完全免费的 A 路径**（本规划默认采用此路径）。

| 方案 | 成本 | URL 样式 | 采用 |
|---|---|---|---|
| **A. Cloudflare 默认 `*.cfargotunnel.com`** | **免费** | `<uuid>.cfargotunnel.com`（64 字符 UUID 丑，但稳定、HTTPS 全自动） | **✅ 采用** |
| B. DuckDNS / 其他免费动态 DNS | 免费 | `xxx.duckdns.org` | ✗ 与 CF Tunnel ingress 匹配要 hack，放弃 |
| C. 自己买域名接 Cloudflare | €1–3 首年 / €10 续费 | `botc-ws.mydomain.xyz` | ✗ 用户不想付费，放弃 |

**A 路径是功能完整的，不是妥协方案**：
- 命名隧道（Named Tunnel）和自定义域名一样稳定
- 自动 HTTPS，自动续证（由 CF 全程管理）
- 带宽无限、请求数无限（CF 明文政策）
- 免费 plan 的 WAF 基础速率限制也能用
- 玩家打开 `https://<username>.github.io/...` 时看不到 WSS 后端 URL 的"丑"，只有代码里能看到
- 未来想换漂亮域名（付费买），Stage 3 改一行 ingress 配置即可迁移，不影响代码

整个规划后文凡提到 `botc-ws.<域名>` 的地方，读者替换成 `<你的-tunnel-uuid>.cfargotunnel.com` 即可。

**切换窗口**（2026-04-23 用户回答）：
> "我们不需要切换窗口。因为我是主持人，我可以控制是否使用这个新的版本，而且我认识我的玩家们"

结论：**Stage 6 简化**——移除"玩家通知期""灰度共存期"。ST 直接切，出问题 ST 自己控场。

**兼容与回退能力**（2026-04-23 用户回答）：
> "当我们目前的服务器（也就是我自己的 NAS）挂掉以后，再回退到原始的那个服务器。因为我不确定我们现在的这个服务器是否可行，也有可能断电。"

结论：**强化 Stage 4**——不能只靠环境变量 + 重新构建。需要**客户端侧自动回退**：
- `socket.js` 先连自建 URL，N 秒无响应或连接失败 → 自动 fallback 到 `wss://live.clocktower.online:8080/`
- 连上之后不做 mid-session failover（避免 session state 撕裂）
- 新增代码块约 20 行，在 Stage 4 明细

**Cloudflare 账号**：用个人账号即可，免费 plan。

**外网测试协助**（2026-04-23 用户回答）：
> "当你需要我做任何从外网进行测试的工作时，可以叫我来帮你做"

结论：Stage 3 / 5 握手验证由用户从工作电脑（外网）发起。

**状态**：Complete — 所有决策已记录

---

### Stage 1 — Cloudflare Tunnel 冒烟测试（60 秒，不动系统）

**目标**：证明"CF Tunnel → fnOS NAS"的通路在这台 NAS 上可用，不部署任何真实服务。

**操作**：
```bash
docker pull cloudflare/cloudflared:latest     # ~30 MB，写入 Docker 本地缓存
# 起一个到一个不存在端口的临时隧道，全程不碰任何真实服务
docker run --rm -d --name cf-smoke \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate --url http://localhost:1
sleep 8 && docker logs cf-smoke 2>&1 | grep trycloudflare.com
# 期望输出：一个 https://xxx-yyy-zzz.trycloudflare.com URL
# 从 Agent 侧 curl 那个 URL，期望收到 CF 的 502（因为 localhost:1 没服务）
# 502 = tunnel 打通，只是背后没服务，符合预期
docker rm -f cf-smoke
```

**成功标准**：
- 镜像拉取成功（输出显示 `Pull complete`）
- 日志中出现 `trycloudflare.com` URL
- `curl` 该 URL 返回 CF 响应（502 / 503 都 OK）
- 容器正常销毁，`docker ps` 无 `cf-smoke`

**不做的事**：
- 不启动任何真实 WSS 服务
- 不绑定任何 NAS 实际端口到公网
- 不配置命名隧道 / 域名
- 不写任何持久文件

**回滚**：`docker rm -f cf-smoke`（容器已 `--rm`）；`docker rmi cloudflare/cloudflared:latest` 回收镜像

**状态**：✅ Complete（2026-04-23）

实测记录：
- `cloudflare/cloudflared@sha256:6b599ca3e974349ead3286d178da61d291961182ec3fe9c505e1dd02c8ac31b0`（2026-03-09 build，63 MB）
- 临时 URL `https://gem-turtle-normally-fewer.trycloudflare.com` 生成成功
- `curl` 返回 `HTTP/2 502` + `server: cloudflare` + `cf-ray: 9f0c0f9db92c1b57-BRU` —— **BRU 边缘（布鲁塞尔）自动命中**，延迟最优
- 容器清理干净，无残留

---

### Stage 2 — Dockerize WSS 后端（局域网验证）

**目标**：`server/index.js` 在容器里跑起来，仅绑 `127.0.0.1:8081`，在 NAS 本机能握手；**LAN 其他机器必须无法连上**。

**交付物**：
- `server/Dockerfile` —— `node:22-alpine` pin to digest，非 root（`USER node`）
- `docker-compose.yml`（仓库根目录）
- `server/.dockerignore`

**关键 compose 配置**：
```yaml
services:
  wss:
    build: ./server
    image: kul-townsquare-wss:local
    container_name: kul-townsquare-wss
    restart: unless-stopped
    environment:
      - NODE_ENV=development   # Stage 2 用明文 ws://，让 compose 里不需要挂 cert
    ports:
      - "127.0.0.1:8081:8081"  # 仅 localhost；LAN 不可达（关键！）
    read_only: true
    tmpfs:
      - /tmp
    cap_drop: [ALL]
    mem_limit: 256m
    cpus: 0.5
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD-SHELL", "node -e \"require('net').connect(8081,'127.0.0.1').on('connect',()=>process.exit(0)).on('error',()=>process.exit(1))\""]
      interval: 30s
      retries: 3
```

**成功标准**：
- `docker compose up -d` 成功，`docker ps` 显示 `healthy`
- NAS 本机 `wscat -c ws://127.0.0.1:8081/<fake-session>` 握手成功
- **另一台局域网机器**（如工作电脑通过 Tailscale 或同 WiFi）`wscat -c ws://192.168.0.112:8081/...` 必须**失败**（connection refused）—— 这是"仅 localhost 绑定"的关键验收
- 容器 `docker exec kul-townsquare-wss id` 返回非 0 uid

**回滚**：`docker compose down && docker rmi kul-townsquare-wss:local`

**状态**：✅ Complete（2026-04-23）

实测记录：
- 镜像 `kul-townsquare-wss:local` 基于 `node:22-alpine@sha256:8ea2348b068a9544dae7317b4f3aafcdc032df1647bb7d768a05a5cad1a7683f`
- 容器 `healthy`；uid=1000、`node` 用户、`ReadonlyRootfs=true`、`CapDrop=[ALL]`、`no-new-privileges=true`、256 MiB、0.5 CPU、PidsLimit=100
- 端口监听 **仅** `127.0.0.1:8081`（`ss -tln` 实测）
- 从 NAS 自身 `bash -c '</dev/tcp/127.0.0.1/8081'` → 成功；`bash -c '</dev/tcp/192.168.0.112/8081'` → `Connection refused`（LAN 不可达确认）
- 实际 WebSocket 握手 `HTTP/1.1 101 Switching Protocols` 成功（带 `Origin: https://example.github.io` 命中现有白名单）
- 容器日志干净，无 error
- 容器保持运行中，供 Stage 3 接入（如需手动停：`docker compose down`）

---

### Stage 3 — 命名 Cloudflare Tunnel + 域名接入

**目标**：用命名隧道把 hostname 路由到容器的 `8081`，容器对 LAN 依然不可见；仅 CF 边缘能进；且非 WSS 路径（如 `/metrics`）前置 404。

**步骤**：

1. 用户在 Cloudflare dashboard 创建 Named Tunnel，取 `TUNNEL_TOKEN`
2. Token 存入 `.env`（权限 600，`.env` 进 `.gitignore`，**不进** Git）
3. **两网络拓扑**（Codex 建议）——不是单一 `botc-net`：
   - `botc-internal`（internal: true 无外网）：wss ↔ cloudflared
   - `cf-egress`：仅 cloudflared，连接 Cloudflare 边缘
   - wss 容器**没有**外网出站能力（即使被 RCE 也打不出 C2）
4. `docker-compose.yml` 新增 `cloudflared` 服务，**与 wss 同等级 hardening**：
   - 镜像 pin digest（如 `cloudflare/cloudflared@sha256:...`）
   - `read_only: true`, `cap_drop: [ALL]`, `security_opt: ["no-new-privileges:true"]`
   - `mem_limit: 128m`, `cpus: 0.25`, `pids_limit: 50`
   - 凭据挂载 `:ro`（`.env` 通过 `env_file:` 方式；或直接挂 `credentials.json` 只读）
   - 日志 `max-size: 10m`, `max-file: 3`
   - `restart: unless-stopped`
5. Wss 容器的 `ports:` 段**彻底移除**（Stage 2 的 `127.0.0.1:8081` 绑定在 Stage 3 撤销；仅通过 `botc-internal` 网络暴露给 cloudflared）
6. Cloudflare dashboard 配 ingress（**按路径分流**，不是 hostname 一刀切）：
   ```
   - hostname: botc-ws.<域名>
     path: "^/[a-z0-9-]{8,64}/[a-z0-9-]{1,32}$"    # /<channel>/<playerId|host>
     service: http://wss:8081
   - hostname: botc-ws.<域名>                       # 任何其他路径，含 /metrics
     service: http_status:404
   - service: http_status:404                       # 其他 hostname 全拒
   ```
   **重要修正**（Codex 指出）：server 代码 `index.js:107-110` URL 格式是 `/<channel>/<playerId>`，**两段**不是一段。我之前写的 `^/[a-zA-Z0-9-]+$` 正则只匹配一段会误杀所有正常玩家握手。
7. WAF 规则（Security → WAF → Rate limiting，免费 plan 可用）：
   - Per-IP：60 requests / minute（WebSocket 握手后不走 HTTP，这条主要拦路径扫描）
   - 免费 plan 允许有限条速率规则 + 基础 WAF managed rules（已够用）
   - Per-IP + per-channel 速率限制需 Worker 或付费 plan → **不做**（免费 plan 走不通）
8. **显式不做**（requirement 3）：不开 Access 登录
9. 容器启动模式：`NODE_ENV=development` + 内部明文 `ws://`；CF 边缘做 TLS termination
   - **不变式**：此模式只有在 compose `ports:` 段**完全不存在**时才安全。compose 文件顶部加断言注释：
     ```yaml
     # INVARIANT: wss service MUST NOT have a `ports:` section.
     # Plain ws:// is safe ONLY because the container is unreachable from host/LAN.
     # Adding `ports:` breaks this invariant and exposes unencrypted WS.
     ```
   - `prom-client` 的 `/metrics` 端点（见 `server/index.js:257-258`）在 production 模式才走 https server；development 模式它**也**在 8081 同一路径暴露。CF ingress 层的 404 拦截是**必须**的第二道防线

**成功标准**：
- 任何外网设备 `wscat -c wss://botc-ws.<域名>/CHANNEL/host` 能握手（回调 Origin `Origin: https://<前端域名>`）
- `ss -tln | grep 8081`：在 NAS host 上**无任何监听**（只有 Docker bridge 内部）
- `curl https://botc-ws.<域名>/metrics` 返回 404（由 CF ingress 拦截，不到达容器）
- `curl https://botc-ws.<域名>/` 返回 404（hostname 根路径也拦）
- `docker inspect kul-townsquare-wss --format '{{json .HostConfig.NetworkMode}}'` 显示 `botc-internal`（无外网）
- Cloudflare dashboard tunnel 状态 GREEN

**回滚**：
- Cloudflare dashboard 删 tunnel（1 分钟）
- `docker compose down`
- 前端无需改动（还在用上游 URL）

**状态**：Not Started

---

### Stage 4 — 前端代码适配 + 后端 origin 白名单 + **自动回退**

**改动清单**（Level 3 —— 动用户契约）：

#### 4.1 `src/store/socket.js` —— 双 URL 客户端级自动回退

现状：
```js
this._wss = "wss://live.clocktower.online:8080/";   // line 3
```

改为：
```js
// Primary = self-hosted on NAS; Fallback = upstream (original).
// Fallback fires ONLY on initial connect failure (connect() catches), never mid-session.
const UPSTREAM_WSS = "wss://live.clocktower.online:8080/";
const SELFHOSTED_WSS = process.env.VUE_APP_WSS_URL || UPSTREAM_WSS;
// Using UPSTREAM as the default when env var absent so open-source build
// doesn't silently route users through the maintainer's NAS. Only a build
// that sets VUE_APP_WSS_URL opts into self-hosting.

this._wssPrimary = SELFHOSTED_WSS;
this._wssFallback = UPSTREAM_WSS;
this._wssCurrent = this._wssPrimary;
this._wssConnectTimeoutMs = 6000;   // 6 s to get WS 101; else fallback
```

`connect(channel)` 方法里包一层 timeout：若 6 秒内没有 `onopen`，关闭 socket、切到 fallback 重试**一次**（不递归）。连上之后 primary 死亡就是死亡——不做 mid-session failover（server 端 channel state 会丢，自动切换反而制造更糟体验）。

**Codex 修正要点**（严重性：高）：
- 默认 fallback **必须**是 `UPSTREAM_WSS`（上游 `clocktower.online`），不是 self-hosted URL。否则任何 fork 此仓库的开源用户会把流量默默路由到我家 NAS。
- 这也意味着：打开源 build = 还是上游；只有 **我** 用 `VUE_APP_WSS_URL=wss://botc-ws.mydomain.xyz/ npm run build` 构建的版本才是自建。

#### 4.2 `server/index.js:25-29` origin 白名单

**现状**（已实测，Codex 指出的精确版本）：
```js
/^https?:\/\/([^.]+\.github\.io|localhost|clocktower\.online|eddbra1nprivatetownsquare\.xyz)/i
```
注意是 `clocktower\.online`（任何子域匹配，含 `live.`），**不是** `live\.clocktower\.online`。

改为（Stage 5 选 B 时需要，选 A 不需要）：
```js
/^https?:\/\/([^.]+\.github\.io|localhost|clocktower\.online|eddbra1nprivatetownsquare\.xyz|botc\.mydomain\.xyz)(:\d+)?\/?$/i
```
修正点：
- 加 `\.` 转义新域名里的点（Codex 指出）
- 改为**完整 origin 匹配**（`(:\d+)?\/?$` 尾锚定），而非前缀匹配——防止类似 `https://clocktower.online.attacker.com` 这种通过前缀 match 的绕过
- **这是原有正则已有的安全缺陷**，借机一并修掉（独立于自建）

#### 4.3 构建配置

`.env.production`（不进 Git，加 `.gitignore`）：
```
VUE_APP_WSS_URL=wss://botc-ws.mydomain.xyz/
```

`.env.example`（进 Git，示例）：
```
# Set this to your self-hosted WebSocket URL to opt into self-hosting.
# Leave blank to use upstream wss://live.clocktower.online:8080/
VUE_APP_WSS_URL=
TUNNEL_TOKEN=
```

#### 4.4 文档

- `server/README.md`：加 "Self-hosted deployment (Cloudflare Tunnel)" 章节，引用本规划
- `CHANGELOG.md` `Unreleased`：一条记录

**成功标准**：
- `npm run lint-ci` 过
- `npm run build`（带 VUE_APP_WSS_URL）成功；`grep -c "botc-ws.mydomain" dist/js/app.*.js` > 0
- `npm run build`（不带 VUE_APP_WSS_URL）成功；生成的 bundle 仍指向 `live.clocktower.online`（验证 fallback 默认）
- 本地 `npm run serve` 接入 Stage 3 域名能握手
- **回退演习**：临时 `docker compose stop wss`，打开前端——6 秒后应自动切到 upstream 并连上；浏览器 devtools 看到 primary 失败 → fallback 成功两次握手尝试

**必须做的审查**：
- Stage 4 代码改完（`socket.js` + `index.js`）→ Codex review
- Agent 执行到此**停下**，等用户批准才提交

**状态**：Not Started

---

### Stage 5 — 前端部署决策

**选项 A —— 前端继续 GH Pages**（推荐，低改动）：
- 改动仅限 `socket.js` 的 URL + `server/index.js` 的 regex（加 github.io 已在白名单里，无需动）
- 工作量：0 额外配置

**选项 B —— 前端也迁 NAS**（用户在历史消息里倾向）：
- 新建 `Dockerfile` 在仓库根目录，用 `caddy:alpine` 服务 `dist/`
- `docker-compose.yml` 增 `frontend` 服务 + CF tunnel ingress 增 `botc.<域名>` → `http://frontend:80`
- 构建流程：CI 或本地 `npm run build && docker compose build frontend`
- 工作量：+1 天

用户回答 Stage 0 问题时确认 A 还是 B。

**状态**：Not Started

---

### Stage 6 — 切换与观察（用户已确认无需通知期）

**前置**：Stage 1–5 全部完成 + ST 亲自跑通至少 1 局完整游戏（含房间创建、身份分发、投票、死亡标记）。

**步骤**：
1. ST 在下一局前部署新前端。**不需要群通知**，因为：
   - 玩家数量可控（你认识他们）
   - Stage 4 自动回退保证"新后端挂了会无感切到老后端"
2. 第一局正式用新后端跑，ST 现场观察任何异常
3. 观察期缩短为 **3 天**（原 7 天，因为失败有自动回退兜底）：
   - 每天快速看 Cloudflare Analytics（WSS 成功率、WAF 拦截）
   - `docker logs kul-townsquare-wss --since 24h | grep -iE 'error|warn|close'`
   - 关注 primary-fallback 触发情况（如果经常触发说明 NAS 不稳，要诊断）

**成功标准**：
- 3 天内 primary 握手成功率 > 99%（Cloudflare Analytics 看）
- 无玩家报告问题（"身份没收到" / "投票失败"等）
- NAS RSS < 300 MiB（`docker stats` 看 wss 容器）

**回滚路径**：
- 方式 A（自动，无人值守）：NAS 挂 → 前端自动切 upstream → ST 无感
- 方式 B（手动，大改出错）：`VUE_APP_WSS_URL= npm run build` 重构建 + 重部署 → 所有人回到上游（< 10 min）

**状态**：Not Started

---

### 安全全局检查清单（贯穿 Stage 2–6）

| # | 项 | 在哪验证 | 达标标志 |
|---|---|---|---|
| 1 | 无入站公网端口 | `ss -tln` on NAS | `0.0.0.0:8081` 和 `192.168.0.112:8081` **没有**监听 |
| 2 | 容器非 root | `docker exec ... id` | uid ≠ 0 |
| 3 | 容器只读根 FS | `docker inspect` | `ReadonlyRootfs: true` |
| 4 | capabilities drop | `docker inspect` | `CapDrop: ["ALL"]` |
| 5 | 资源限制 | `docker inspect` | `Memory: 268435456`（256 MiB） |
| 6 | 凭据文件权限 | `ls -l .env` | `-rw------- 1 user user` |
| 7 | `.env` 不在 Git | `git check-ignore .env` | 返回 `.env` |
| 8 | `/metrics` 不对外 | `curl https://botc-ws.<域名>/metrics` | HTTP 404 |
| 9 | WAF rate limit 生效 | Cloudflare dashboard Security | "Rate limiting" 规则显示 active |
| 10 | 日志不爆盘 | `docker compose config` | `max-size: 10m` 存在 |
| 11 | 镜像 pin digest | Dockerfile + compose | `FROM node:22-alpine@sha256:...` |
| 12 | Cloudflared 凭据挂载只读 | `docker inspect cloudflared` | volume mode `ro` |

---

---

### 凭据与恢复（Codex 补）

**Tunnel Token 丢失场景**：
- 现象：`.env` 被误删 / 磁盘损坏 / 备份缺失
- 恢复步骤：
  1. Cloudflare dashboard → Zero Trust → Networks → Tunnels → 选中 tunnel → "Rotate credentials"
  2. 下载新 token，覆盖写入 `.env`（权限 600）
  3. `docker compose restart cloudflared`
  4. Tunnel UUID 保持不变，DNS 不用改
- **预防**：`.env` 做加密备份（`gpg --symmetric .env > .env.gpg` 放 NAS 另一块盘或云盘）

**监控告警**（Codex 建议）：
- Cloudflare 侧：dashboard → Notifications → 加 "Tunnel Health: Unhealthy" 邮件通知（免费）
- 本地侧：`docker-compose.yml` 的 healthcheck 失败重启可见于 `docker events`；可选加一个小脚本 cron 检查 `docker inspect --format '{{.State.Health.Status}}' kul-townsquare-wss`，异常时推 Bark / Telegram bot（留 Stage 6+ 待办）

---

### 待确认事项

- [x] Stage 0 的所有问题（用户 2026-04-23 回答完毕）
- [ ] Stage 5 A vs B（Codex 建议 A；等用户最终拍板）
- [x] Codex review on 本规划文档（已完成 2026-04-23，意见已吸收到本版）
- [ ] Codex review on Stage 4 代码改动（代码改完再调）

---

### Codex 审查（2026-04-23）发现与对应修订

| 级别 | 发现 | 对应修订 |
|---|---|---|
| Must-fix | WAF 正则 `^/[a-zA-Z0-9-]+$` 与实际协议 `/<channel>/<playerId>` 不符 | Stage 3 步骤 6 改为双段正则 `^/[a-z0-9-]{8,64}/[a-z0-9-]{1,32}$` |
| Must-fix | Hostname-wide ingress 未拦 `/metrics` | Stage 3 步骤 6 按路径分流，非协议路径前置 404 |
| Must-fix | Fallback URL 指向自建，污染开源 build | Stage 4.1 修正默认 fallback = `UPSTREAM_WSS` |
| Must-fix | 引用的 `verifyClient` 旧正则不对 | Stage 4.2 已用实测版本替换 |
| Must-fix | 明文 ws 不变式未显式化 | Stage 3 步骤 9 加 compose 断言注释 |
| Should | 单一 Docker 网络给 wss 不必要的外网出站 | Stage 3 步骤 3 改双网络拓扑 |
| Should | cloudflared sidecar 无 hardening | Stage 3 步骤 4 加同级 hardening |
| Should | `cloudflare/cloudflared:latest` 会漂 | Stage 1 冒烟也 pin digest |
| Should | 无凭据恢复流程 | 新增"凭据与恢复"节 |
| Should | 只有每日人工看日志 | 新增告警节 |
| Should | Stage 6 SLA 对 option B 未定义 | Stage 6 分两类回滚路径 |
| Should | session ID 猜测防护依赖熵 | Stage 5+ 待办：评估现有 session ID 熵 |
| Nice | Stage 5 选 A 还是 B | Codex 推荐 A；用户决 |
| Nice | `pids_limit` | Stage 3 步骤 4 已含 |

Codex 已确认正确的部分：三条硬约束满足、CF TLS termination 的设计合理、Stage 2 localhost 绑定方向正确、Stage 3 撤 ports 段方向正确。

---

### 完成记录

（未完成）

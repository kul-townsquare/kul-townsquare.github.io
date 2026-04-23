---
name: 自建部署基础设施现状
description: BotC Live Session 自建后端的实际部署状态、架构决策、凭据位置、关键命令
type: project
---

# 自建部署现状（2026-04-23 锁定）

## 架构决策（已敲定，非规划）

```
 [玩家浏览器]
     │ wss://botc-ws.kul-botc.eu.org/chan/host
     ▼
 [Cloudflare 边缘]
     │ Named Tunnel
     ▼
 [NAS: /usr/bin/cloudflared systemd 服务 (root)]
     │ http://localhost:8081
     ▼
 [NAS: Docker 容器 kul-townsquare-wss]
     │ 127.0.0.1:8081 (ports binding)
     │ NODE_ENV=development
     │ uid=1000 node, read_only, cap_drop ALL
     ▼
 [Node 进程 server/index.js, ws:8081]
```

## 关键身份

| 项 | 值 |
|---|---|
| 域名 | `kul-botc.eu.org` |
| eu.org 账号 | `ZN196-FREE` |
| CF NS pair | `oaklyn.ns.cloudflare.com`, `piotr.ns.cloudflare.com` |
| CF tunnel ID | `23ea2f26-4ce8-4202-a77b-744b80713b1f`（从 token 解码，可在 dashboard 确认） |
| NAS LAN IP | `192.168.0.112` |
| NAS 公网出站 IP | `94.224.114.159`（比利时 Proximus/Telenet，动态，可能变） |
| 容器名 | `kul-townsquare-wss` |
| 镜像标签 | `kul-townsquare-wss:local`（本地 build，非 registry） |

## 凭据位置

- **CF Tunnel token**：`/etc/systemd/system/cloudflared.service` 的 `ExecStart` 命令行里（`ps aux` 可见，NAS 全体用户可见但全可信）
- **CF 账号**：用户个人邮箱（Gmail），2FA 已开
- **eu.org 账号**：同一邮箱
- **无 `.env` 文件** —— cloudflared 官方安装脚本不走 `.env`

## 已应用的安全配置

**wss 容器**（`docker-compose.yml` 定义）：
- ✓ 非 root（uid 1000 `node`）
- ✓ `read_only: true` 根文件系统
- ✓ `tmpfs: /tmp:size=16m,noexec,nosuid,nodev`
- ✓ `cap_drop: [ALL]`
- ✓ `security_opt: [no-new-privileges:true]`
- ✓ `mem_limit: 256m`, `cpus: 0.5`, `pids_limit: 100`
- ✓ 端口仅 `127.0.0.1:8081`（Stage 3 会移除本绑定，改走 cloudflared 内部）
- ✓ 日志 json-file max-size 10m max-file 3
- ✓ TCP healthcheck

**cloudflared**（systemd 服务）：
- ✓ 自动更新启用（B 补强，移除了 `--no-autoupdate`）
- ⚠ 以 root 运行（CF 官方默认；用户可信场景下接受）
- ⚠ token 写命令行（`ps aux` 可见；未做 token 文件化补强 A，可后补）
- ✓ `Restart=on-failure`

**Cloudflare 账号**：
- ✓ 2FA 启用
- ✓ 免费 plan（够用）

## 关键命令备忘

```bash
# 容器状态
docker compose ps
docker logs kul-townsquare-wss --tail 20

# 容器操作（在仓库根目录跑）
docker compose up -d
docker compose down
docker compose build --pull

# cloudflared 状态
systemctl status cloudflared
journalctl -u cloudflared -f         # 需 sudo 看实时日志

# 验证端口绑定（核心安全不变式）
ss -tln | grep 8081
# 必须只出现 127.0.0.1:8081，不能出现 0.0.0.0:8081 或 192.168.0.112:8081

# 验证 NAS 本机可达 / LAN 不可达
bash -c '</dev/tcp/127.0.0.1/8081' && echo OK          # 应成功
bash -c '</dev/tcp/192.168.0.112/8081' || echo refused  # 应失败

# 前端 lint
npm run lint-ci

# 剧本校验
python3 validate_scripts.py --summary

# 规则同步（编辑 .agent-rules/ 后）
python3 .agent-rules/sync_agent_rules.py
```

## 不变式（破坏任一条都是事故）

1. `docker-compose.yml` 的 wss 服务**不得**出现 `0.0.0.0:8081:8081`——只能是 `127.0.0.1:8081:8081` 或 Stage 3 后完全删掉 `ports:` 段
2. `NODE_ENV` 在容器里**必须**是 `development`（否则需 cert 文件且暴露 metrics）
3. `server/index.js:28` 的 `verifyClient` 正则只接 origin 白名单内域名，不放行任何其他 origin
4. `socket.js:3` 的 `this._wss` 默认值（环境变量未设时）**必须**是上游 `wss://live.clocktower.online:8080/`——保护 fork 本仓库的其他用户不会被默默路由到本 NAS
5. `kul-botc.eu.org` zone 在 CF 的 NS 必须是用户拿到的 `oaklyn` + `piotr`——换 zone 或换 NS pair 需同步到 eu.org registry
6. 不推任何代码到 `main` 分支——线上生产环境由用户手动运维

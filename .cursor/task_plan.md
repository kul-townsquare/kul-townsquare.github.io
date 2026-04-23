# 任务进度跟踪

最近更新：2026-04-23

## 总体目标

把 Live Session WebSocket 后端从上游 `wss://live.clocktower.online:8080/` 迁到用户自己的 fnOS NAS（比利时），通过 Cloudflare Tunnel 暴露，保持玩家零安装。

完整设计见 `.planning/20260423_self_host_ws_server.md`。

## 阶段状态

| Stage | 名称 | 状态 | 备注 |
|---|---|---|---|
| 0 | 前置决策 | ✅ done | 免费路径、无切换窗口、客户端自动回退 |
| 1 | CF Tunnel 冒烟测试 | ✅ done | BRU 边缘，`trycloudflare.com` 临时 URL 返回 CF 502，通路验证 |
| 2 | Dockerize WSS 后端 | ✅ done | 容器 healthy、127.0.0.1 绑定、LAN 不可达已验证、Codex 修复项已应用 |
| 3 | 命名 Tunnel + 域名接入 | ⏸ **blocked** | **等 `kul-botc.eu.org` eu.org 审批（1–2 周到数月）** |
| 4 | 前端代码适配（socket.js + verifyClient + 自动回退） | ⏳ planned | Stage 3 完成后开始 |
| 5 | 前端部署决策（A/B） | ⏳ planned | Stage 4 完成后择一（Codex 推荐 A：前端留 GH Pages） |
| 6 | 切换 | ⏳ planned | 用户为 ST，无需通知期 |

## 当前阻塞

**eu.org 人工审批 `kul-botc.eu.org`**：
- 申请人：用户账号 `ZN196-FREE`
- 申请日期：2026-04-23
- 预期等待：1 周到数月（社区志愿者维护，队列长）
- 联系方式：`majordomo@lists.eu.org`（仅邮件列表，无人工支持）

## 恢复会话时的优先动作

会话重启（或新 AI 接手）时，按此顺序：

1. **读本文件** + `.cursor/progress.md` + `.cursor/findings.md`
2. **读** `.planning/20260423_self_host_ws_server.md`（完整规划）
3. **问用户**：`kul-botc.eu.org` 是否已被 eu.org 批准？
   - 验证方式：`dig +short NS kul-botc.eu.org` 如返回 `*.ns.cloudflare.com`，则已批准
   - 或 CF dashboard 看 zone 状态是否由 Pending 变成 Active
4. 根据回答：
   - **已批准** → 进 Stage 3 收尾（见 `.planning/` 里的 "待完成部分"）
   - **未批准** → 继续等；确认其他可并行工作（比如 Stage 4 的代码准备可以在没有 tunnel 的情况下预先写，走 mock）

## 同期未做 / 待考虑

- 安全补强 A（token 文件化）：可选，用户已接受当前 root 运行 + token 在 `ps aux` 可见；如未来引入不可信本地账户再补
- Stage 3 "WAF rate limit per channel" 需要 Cloudflare Worker 或付费 plan，当前不做
- 验证 Script Tool 与当前 fork 的兼容性（早期发现的 P0 候选，后来用户澄清中文社区不用 Script Tool，降级为低优先级）
- 拆 god component（`Player.vue` 983 行、`socket.js` 954 行、`ReferenceModal.vue` 958 行）—— 长期重构，与本次迁移独立

## 绝对不可做（规则归档）

- 不得推任何分支到 `main`（生产线上分支）
- `vibe-dev` 分支的 push 需用户明确批准
- 不得擅自 `docker compose down` 用户正在用的服务
- 不得改 `server/index.js` 的用户契约（`verifyClient` 正则、URL 路径格式）除非走 Level 3 规划 + 用户批准

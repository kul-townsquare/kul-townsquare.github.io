#!/usr/bin/env python3
"""Sync canonical agent rules from .agent-rules/ to tool-specific config files.

Usage:
    python3 .agent-rules/sync_agent_rules.py

Targets generated (in repo root):
    CLAUDE.md                    Claude Code entry point
    AGENTS.md                    Generic AI agents (Codex, etc.)
    .cursor/rules/00_synced.mdc  Cursor global rules (alwaysApply)

Source of truth:
    .agent-rules/approval.md   task approval policy
    .agent-rules/core.md       project identity, stack, directory, user contracts
    .agent-rules/style.md      code style, Git workflow, quality gates

Edit the source files, then re-run this script. The generated files carry an
AUTO-GENERATED banner; do not hand-edit them.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
RULES_DIR = REPO_ROOT / ".agent-rules"
PROJECT_NAME = "kul-townsquare.github.io"


def load_canonical() -> str:
    files = sorted(f for f in RULES_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No .md files found in {RULES_DIR}")
    sections = [f.read_text(encoding="utf-8").strip() for f in files]
    return "\n\n---\n\n".join(sections)


SYNC_NOTE = (
    "<!-- AUTO-GENERATED — edit .agent-rules/*.md and run "
    "`python3 .agent-rules/sync_agent_rules.py` to update -->"
)

CLAUDE_HEADER = f"""\
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

{SYNC_NOTE}

## 项目速览

**{PROJECT_NAME}** —— 《染：钟楼谜团》（Blood on the Clocktower）说书人辅助程序。Vue 2 前端 + Node WebSocket 后端，GitHub Pages 部署，GPL-3.0 开源。完整背景见下方「项目核心规则」。

## 常用命令

```bash
# 本地开发服务器（热重载）
npm run serve

# 生产构建（产物在 dist/，⚠ 不提交）
npm run build

# Lint（带 auto-fix，日常使用）
npm run lint

# Lint CI 门禁（无 fix，零警告）—— PR 前必须通过
npm run lint-ci

# 数据维护脚本（根目录 .py 示例）
python3 add_edition_and_roles.py
python3 download_icons.py

# 同步本文件 + AGENTS.md + .cursor/rules/00_synced.mdc（编辑 .agent-rules/ 后运行）
python3 .agent-rules/sync_agent_rules.py
```

权限详见 `.claude/settings.local.json`。

## Codex 代码审查（Claude Code 专用调用）

当下方「代码审查（Codex Review Gate）」触发条件满足时，用以下 MCP 工具调用 Codex：

```
mcp__codex__codex({{
  prompt: "<审查要求 + 改动摘要 + 需关注的审查重点>",
  sandbox: "read-only",
  cwd: "<项目根目录>"
}})
```

- **始终**使用 `sandbox: "read-only"`（审查不改代码）
- 追问使用 `mcp__codex__codex-reply`，传入上一次的 `threadId`
- prompt 内容建议包含：
  - 本次改动的目的（link 到 `.planning/` 规划文档或 issue）
  - 涉及的文件列表 + 对应的用户契约
  - 希望 Codex 重点看的风险点（如 WebSocket 新消息的向后兼容）
  - 本项目的 ESLint + Vue 2 约定（见下方「代码规范」节）

---
"""

AGENTS_HEADER = f"""\
# {PROJECT_NAME} — AI Coding Agent 指令

{SYNC_NOTE}

> 适用于 Claude Code / Codex / Cursor 等所有 AI coding agent。
> Cursor 用户另见 `.cursor/rules/00_synced.mdc` 获取同份规则。
> 规则修改请编辑 `.agent-rules/*.md` 后运行 `python3 .agent-rules/sync_agent_rules.py`。

---
"""

CURSOR_FRONTMATTER = f"""\
---
description: >-
  {PROJECT_NAME} 全局规则（Auto-synced from .agent-rules/）
  编辑 .agent-rules/*.md 后运行 python3 .agent-rules/sync_agent_rules.py
alwaysApply: true
---

"""


def write_if_changed(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        print(f"  [unchanged] {path.relative_to(REPO_ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"  [updated]   {path.relative_to(REPO_ROOT)}")


def main() -> None:
    canonical = load_canonical()
    md_files = sorted(f for f in RULES_DIR.glob("*.md"))
    print(f"Loaded {len(md_files)} canonical files from .agent-rules/\n")

    targets = [
        (REPO_ROOT / "CLAUDE.md",                   CLAUDE_HEADER + canonical + "\n"),
        (REPO_ROOT / "AGENTS.md",                   AGENTS_HEADER + canonical + "\n"),
        (REPO_ROOT / ".cursor/rules/00_synced.mdc", CURSOR_FRONTMATTER + canonical + "\n"),
    ]

    print("Syncing:")
    for path, content in targets:
        write_if_changed(path, content)

    print("\nDone. Commit all changed files together.")


if __name__ == "__main__":
    main()

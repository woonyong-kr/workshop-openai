# Cleanmail Workspace

Public Gmail cleanup service worktree for concurrent agents.

## What stays in this repo

- `apps/web`: Next.js web shell for landing, dashboard, auth callbacks, and API routes.
- `packages/contracts`: shared domain and API types. All agents should depend on these first.
- `packages/gmail-core`: reserved package for scan, grouping, classification, and unsubscribe parsing.
- `packages/auth-core`: reserved package for Google OAuth, session, and token encryption.
- `packages/data-core`: reserved package for Postgres schema, repositories, and audit logging.
- `skills/gmail-mailbox-cleanup`: reference implementation and heuristics to port, not runtime code.

## Parallel work rule

1. Change shared types in `packages/contracts` first.
2. Keep `apps/web` focused on presentation and route composition.
3. Implement Gmail logic, auth, and persistence in their own packages to reduce merge conflicts.
4. Read [docs/ARCHITECTURE.md](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md), [docs/TASK_BOARD.md](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md), and [docs/AGENT_MESSAGES.md](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/AGENT_MESSAGES.md) before starting.

## Quick start

```bash
pnpm install
pnpm dev:web
```

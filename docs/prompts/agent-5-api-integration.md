# Agent Prompt: API Integration

You are taking `T08-api-integration` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Connect the Next.js API routes to the shared auth, Gmail, and data packages.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T08-api-integration.md`

## Scope

- Edit `apps/web/src/app/api/**`
- Edit `apps/web/src/**` if route composition needs local helpers
- Edit `packages/contracts/**` only if a route contract gap blocks you

## Required outputs

- `POST /api/scan`
- `GET /api/scan/:jobId`
- `POST /api/cleanup/preview`
- `POST /api/cleanup/execute`

## Constraints

- use shared packages rather than reimplementing logic
- execute requires explicit confirmation and idempotency key
- responses must match `@cleanmail/contracts`

## Report back with

1. changed files
2. endpoints wired
3. tests run
4. unresolved dependencies

# Agent Prompt: Shared Contracts

You are taking `T01-contracts-baseline` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Define the shared TypeScript contracts that every other agent can build against without inventing local duplicates.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T01-contracts-baseline.md`

## Scope

- Only edit `packages/contracts/**`

## Required outputs

- auth session and connected-account summaries
- scan job create and poll payloads
- sender group summary and review-detail payloads
- preview and execute request/response payloads
- audit log summary payloads
- UI-friendly enums and status types

## Constraints

- v1 supports `trash` and `unsubscribe` only
- do not add hard-delete public actions
- metadata-only data model
- exported names should be reusable by UI, API routes, and server packages

## Report back with

1. changed files
2. new exported types/constants
3. blockers or assumptions
4. which downstream tasks are now unblocked

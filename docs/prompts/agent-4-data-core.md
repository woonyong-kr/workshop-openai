# Agent Prompt: Data Core

You are taking `T05-data-schema` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Design the Postgres schema and repository layer for users, accounts, scan jobs, grouped mail, execution runs, and purge support.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T05-data-schema.md`

## Scope

- Edit `packages/data-core/**`
- Edit `packages/contracts/**` only if a missing shared type blocks you

## Required outputs

- schema/table definitions
- repository interfaces
- execution idempotency support
- 24-hour metadata purge support

## Constraints

- metadata and snippets only
- no full body or attachments
- design for Vercel Postgres / Neon

## Report back with

1. changed files
2. schema summary
3. repository surface
4. follow-up tasks unblocked

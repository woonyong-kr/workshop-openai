# Agent Prompt: Gmail Core

You are taking `T03-gmail-grouping` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Port the sender grouping, classification, and unsubscribe parsing logic from the Python reference into TypeScript library code.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T03-gmail-grouping.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/skills/gmail-mailbox-cleanup/scripts/gmail_cleanup.py`

## Scope

- Edit `packages/gmail-core/**`
- Edit `packages/contracts/**` only if a missing shared type blocks you

## Required outputs

- sender normalization
- sender-type heuristics
- classification scoring
- unsubscribe parser for HTTP and `mailto:`
- grouped summary builder from message metadata

## Constraints

- metadata only
- no live Gmail calls in this task
- keep functions deterministic and testable

## Report back with

1. changed files
2. exported functions
3. tests run
4. contract changes or blockers

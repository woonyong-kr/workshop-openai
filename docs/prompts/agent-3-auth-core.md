# Agent Prompt: Auth Core

You are taking `T04-auth-session` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Implement reusable Google OAuth and application-session primitives for the web app.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T04-auth-session.md`

## Scope

- Edit `packages/auth-core/**`
- Edit `packages/contracts/**` only if a missing shared type blocks you

## Required outputs

- OAuth URL builder
- state and nonce helpers
- callback exchange interfaces
- session cookie helpers
- refresh-token encryption interfaces
- connected-account consent status model

## Constraints

- fixed staging and app domains for redirects
- scopes limited to profile, email, `gmail.modify`, and `gmail.send`
- keep framework coupling low

## Report back with

1. changed files
2. exported functions/interfaces
3. env vars expected
4. unresolved security questions

# Agent Prompt: Web Shell

You are taking `T02-web-shell` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

## Mission

Build the landing page and signed-in dashboard shell so the Gmail cleanup flow is visible end-to-end before backend integration.

## Read first

- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T02-web-shell.md`

## Scope

- Only edit `apps/web/**`

## Required outputs

- landing page
- signed-in dashboard shell
- left sidebar with `전체 정리`
- sender-group review layout
- preview modal shell and execution result shell

## Constraints

- consume `@cleanmail/contracts`
- do not define route payloads locally unless you first update `packages/contracts`
- do not embed Gmail parsing, OAuth crypto, or DB code in the web layer

## Report back with

1. changed files
2. screenshots or route summary
3. contract gaps you found
4. follow-up tasks unblocked

# Task Board

Use this board to assign work without stepping on other agents.

## Claim Rules

1. Pick a task with `Status: READY`.
2. Stay inside the listed `Allowed paths`.
3. If you need a new shared type, update `packages/contracts` first.
4. Do not edit `skills/gmail-mailbox-cleanup`; it is reference material only.
5. Report back with changed files, test results, and follow-up needs.

## Ready Now

| Task | Status | Owner lane | Depends on | Allowed paths | Prompt | Output |
| --- | --- | --- | --- | --- | --- | --- |
| `T01-contracts-baseline` | DONE | Shared | none | `packages/contracts/**` | `docs/prompts/agent-0-contracts.md` | stable enums and API payloads |
| `T02-web-shell` | READY | Agent 1 | `T01` soft dependency | `apps/web/**` | `docs/prompts/agent-1-web-shell.md` | landing and dashboard shell |
| `T03-gmail-grouping` | READY | Agent 2 | `T01` soft dependency | `packages/gmail-core/**` | `docs/prompts/agent-2-gmail-core.md` | sender grouping and classification core |
| `T04-auth-session` | READY | Agent 3 | `T01` soft dependency | `packages/auth-core/**` | `docs/prompts/agent-3-auth-core.md` | Google OAuth and session primitives |
| `T05-data-schema` | READY | Agent 4 | `T01` soft dependency | `packages/data-core/**` | `docs/prompts/agent-4-data-core.md` | Postgres schema and repositories |

## Starts After Core Tasks

| Task | Status | Owner lane | Depends on | Allowed paths | Prompt | Output |
| --- | --- | --- | --- | --- | --- | --- |
| `T06-scan-preview-execute` | BLOCKED | Agent 2 | `T03`, `T05` | `packages/gmail-core/**`, `packages/contracts/**` | `docs/prompts/agent-2-gmail-core.md` | scan and cleanup planner |
| `T07-review-ui` | BLOCKED | Agent 1 | `T01`, `T03` | `apps/web/**`, `packages/contracts/**` | `docs/prompts/agent-1-web-shell.md` | group table, checkbox flow, preview modal |
| `T08-api-integration` | BLOCKED | Agent 5 | `T03`, `T04`, `T05` | `apps/web/src/app/api/**`, `packages/contracts/**` | `docs/prompts/agent-5-api-integration.md` | route handlers using real services |
| `T09-launch-docs` | BLOCKED | Agent 6 | `T04`, `T05` | `docs/**`, `apps/web/src/app/**` | `docs/prompts/agent-6-launch-docs.md` | privacy, terms, env setup, deploy notes |

## Suggested Parallel Start

- Agent 1: `T02-web-shell`
- Agent 2: `T03-gmail-grouping`
- Agent 3: `T04-auth-session`
- Agent 4: `T05-data-schema`
- Shared owner: `T01-contracts-baseline` as the first short pass

## Definition of Done

- Task scope stays inside allowed paths.
- Shared contracts compile for all packages that import them.
- No placeholder API shape is invented outside `packages/contracts`.
- Handoff includes unresolved risks and exact next tasks unblocked.

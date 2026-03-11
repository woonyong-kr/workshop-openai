# Agent Pickup Messages

Copy one message and send it to another coding agent.

Full prompt files live under `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/prompts/`.

## Message: T01 Contracts

You own `T01-contracts-baseline` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md`
- Only edit `packages/contracts/**`
- Define the minimum stable shared contracts for auth, scan jobs, sender groups, preview, execute, audit log summaries, and UI view models
- Keep v1 limited to trash plus unsubscribe
- Do not touch `skills/gmail-mailbox-cleanup/**`
- Return changed files, contract summary, and any downstream tasks you unblocked

## Message: T02 Web Shell

You own `T02-web-shell` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T02-web-shell.md`
- Only edit `apps/web/**`
- Build the landing page, app shell, sidebar, and dashboard placeholders around the `전체 정리` flow
- Consume contracts from `@cleanmail/contracts`; do not invent route payloads locally
- Do not implement Gmail parsing, OAuth crypto, or persistence inline
- Return changed files, screenshots if you produced them, and any contract gaps

## Message: T03 Gmail Core

You own `T03-gmail-grouping` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T03-gmail-grouping.md`
- Only edit `packages/gmail-core/**` and, if necessary, `packages/contracts/**`
- Port sender normalization, grouping, classification heuristics, and unsubscribe parsing from `skills/gmail-mailbox-cleanup/scripts/gmail_cleanup.py`
- Keep logic metadata-only; no full body handling
- Return changed files, exported functions, tests run, and any contract changes you needed

## Message: T04 Auth Session

You own `T04-auth-session` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T04-auth-session.md`
- Only edit `packages/auth-core/**` and, if necessary, `packages/contracts/**`
- Implement Google OAuth URL generation, callback exchange helpers, session cookie primitives, consent-state modeling, and refresh-token encryption interfaces
- Assume fixed staging and app domains for OAuth redirects
- Return changed files, env vars expected, and unresolved security questions

## Message: T05 Data Schema

You own `T05-data-schema` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/ARCHITECTURE.md`
- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T05-data-schema.md`
- Only edit `packages/data-core/**` and, if necessary, `packages/contracts/**`
- Design the Postgres schema and repositories for users, encrypted OAuth accounts, scan jobs, sender groups, execution runs, and purge support
- Store metadata only; never full body or attachments
- Return changed files, schema summary, and follow-up tasks for API integration

## Message: T06 Scan Preview Execute

You own `T06-scan-preview-execute` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T06-scan-preview-execute.md`
- Only edit `packages/gmail-core/**` and `packages/contracts/**` if strictly required
- Build scan orchestration, preview aggregation, and execute planning on top of the core grouping logic
- Keep side effects separated from planning so route handlers can preview safely
- Return changed files, planning API summary, and outstanding integrations

## Message: T08 API Integration

You own `T08-api-integration` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T08-api-integration.md`
- Only edit `apps/web/src/app/api/**`, `apps/web/src/**`, and `packages/contracts/**` if required
- Wire `auth-core`, `gmail-core`, and `data-core` into `POST /api/scan`, `GET /api/scan/:jobId`, `POST /api/cleanup/preview`, and `POST /api/cleanup/execute`
- Enforce explicit confirmation and idempotency on execute
- Return changed files, route contract summary, and test results

## Message: T09 Launch Docs

You own `T09-launch-docs` in `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai`.

- Read `/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T09-launch-docs.md`
- Only edit `docs/**` and `apps/web/src/app/**`
- Add privacy, terms, support, environment setup, and Google OAuth plus Vercel launch documentation
- Keep the docs aligned with fixed OAuth domains and v1 scope limits
- Return changed files and a checklist of anything still needed before staging

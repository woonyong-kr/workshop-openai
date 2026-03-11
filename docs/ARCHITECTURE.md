# Architecture Boundary

## Objective

Build a public Gmail cleanup SaaS that uses Google OAuth, scans Gmail metadata, groups mail by sender, recommends cleanup actions, and executes trash plus unsubscribe after explicit confirmation.

## Repo boundary

- `apps/web`
  - Owns the Next.js app shell, landing page, sidebar/dashboard shell, route handlers, and UI states.
  - Must not reimplement Gmail parsing or token crypto inline.
- `packages/contracts`
  - Owns shared enums, API payloads, and cross-package types.
  - Any schema change starts here.
- `packages/gmail-core`
  - Owns Gmail query defaults, sender normalization, classification heuristics, unsubscribe extraction, and scan orchestration rules.
  - Port source material from `skills/gmail-mailbox-cleanup`.
- `packages/auth-core`
  - Owns Google OAuth URL generation, callback exchange, session cookie helpers, refresh token encryption, and consent-state handling.
- `packages/data-core`
  - Owns Postgres tables, repositories, scan job persistence, execution logs, and purge helpers.
- `skills/gmail-mailbox-cleanup`
  - Reference-only directory containing Python and Apps Script logic to port.

## Integration order

1. Lock shared contracts.
2. Implement `gmail-core`, `auth-core`, and `data-core` in parallel.
3. Wire packages into `apps/web` once contracts settle.
4. Add Google/Vercel deployment config after the app shell and server packages stabilize.

## Shared constraints

- v1 scope is `trash + unsubscribe`; no hard delete.
- Store metadata only, never full body or attachments.
- AI classification remains opt-in and consumes sender, subject, header, label, and snippet data only.
- Random Vercel preview URLs are for UI QA only; OAuth uses fixed staging and app domains.

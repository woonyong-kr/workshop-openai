# Web App

Next.js app shell for the Cleanmail service.

## Responsibilities

- landing page and marketing copy
- dashboard layout and sidebar
- auth callback routes and API composition
- cleanup review UI
- policy pages needed for Google verification

## Local run

```bash
pnpm install
pnpm dev:web
```

## Contract rule

Do not invent route payloads in `apps/web`. Add or change them in `packages/contracts` first.

## Pairing guidance

- Agent 1 can build UI immediately against `packages/contracts`.
- Agent 4 should own API route composition after `auth-core`, `gmail-core`, and `data-core` settle.

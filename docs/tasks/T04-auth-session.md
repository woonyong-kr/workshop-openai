# T04 Auth Session

## Goal

Implement the reusable auth primitives for Google OAuth and application sessions.

## Allowed paths

- `packages/auth-core/**`
- `packages/contracts/**` only if a shared auth type is missing

## Required outputs

- Google OAuth URL builder
- state and nonce helpers
- callback token exchange helper interfaces
- session cookie encode/decode helpers
- refresh token encryption interface and key requirements
- consent status model for connected Gmail accounts

## Constraints

- assume fixed `staging` and `app` domains for redirect URIs
- request scopes only for profile, email, `gmail.modify`, and `gmail.send`
- keep framework coupling low so route handlers can call the package from Next.js

## Done when

- API route work can authenticate a user and persist a connected Gmail account without adding new core auth decisions

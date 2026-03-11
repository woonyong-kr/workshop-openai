# T01 Contracts Baseline

## Goal

Define the shared contracts that every other task can safely build against.

## Allowed paths

- `packages/contracts/**`

## Required outputs

- scan job types for create and poll
- sender group summary and detailed review types
- cleanup preview and execute request/response types
- auth session and connected-account summary types
- audit log and execution result summary types

## Constraints

- v1 only supports `trash` and `unsubscribe`
- no hard delete fields in public request payloads
- metadata-only storage model
- types should be reusable by both UI and API handlers

## Done when

- contracts are coherent enough that `apps/web`, `gmail-core`, `auth-core`, and `data-core` can import them without inventing their own duplicates
- exported names are obvious and stable

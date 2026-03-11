# T05 Data Schema

## Goal

Design the persistence layer for users, connected accounts, scans, grouped results, execution logs, and metadata retention.

## Allowed paths

- `packages/data-core/**`
- `packages/contracts/**` only if a shared persistence-facing type is missing

## Required outputs

- schema or table definitions for user, account, scan job, sender group, execution run, and execution event
- repository interfaces and base implementations
- retention helpers for 24-hour metadata purge
- idempotency support for cleanup execution

## Constraints

- store metadata and snippets only
- no full message body or attachments
- design for Vercel Postgres / Neon compatibility

## Done when

- route handlers can create scans, persist grouped results, preview execution, and record outcomes using stable repository calls

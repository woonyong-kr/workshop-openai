# T08 API Integration

## Goal

Connect the web app API routes to the shared packages once contracts and core services exist.

## Allowed paths

- `apps/web/src/app/api/**`
- `apps/web/src/**`
- `packages/contracts/**` only if a final route contract gap blocks you

## Required outputs

- `POST /api/scan`
- `GET /api/scan/:jobId`
- `POST /api/cleanup/preview`
- `POST /api/cleanup/execute`

## Constraints

- routes must call shared services rather than reimplementing domain logic
- execute must require an idempotency key
- responses must follow `packages/contracts`

## Done when

- the UI can hit all four endpoints against real package implementations without local mocking

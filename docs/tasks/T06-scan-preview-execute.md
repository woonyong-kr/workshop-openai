# T06 Scan Preview Execute

## Goal

Build the scan orchestration and cleanup planning layer on top of the Gmail grouping core.

## Allowed paths

- `packages/gmail-core/**`
- `packages/contracts/**` only if a missing planner type blocks progress

## Required outputs

- paginated scan orchestrator with default query and batch size
- preview calculator for selected sender groups
- execute plan builder separating trash, HTTP unsubscribe, `mailto:` unsubscribe, and skipped actions
- partial-failure result modeling

## Constraints

- side effects should be isolated so preview remains pure
- execution planning must respect explicit selected groups only
- no hard delete support in v1

## Done when

- API integration can ask for preview counts and a concrete execution plan without duplicating logic

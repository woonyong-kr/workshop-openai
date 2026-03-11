# T07 Review UI

## Goal

Turn the web shell into a real cleanup review experience once sender-group contracts and grouping outputs exist.

## Allowed paths

- `apps/web/**`
- `packages/contracts/**` only if a UI-facing type is missing

## Required outputs

- sender-group table or list with selection controls
- bulk select and per-group selection state
- preview summary panel or modal
- execution confirmation state and result rendering

## Constraints

- consume shared contracts from `packages/contracts`
- do not duplicate grouping logic in the UI
- assume preview and execute are separate API calls

## Done when

- a signed-in user can review suggested cleanup groups, choose exact groups, preview counts, and understand the execute step

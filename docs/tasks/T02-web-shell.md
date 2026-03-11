# T02 Web Shell

## Goal

Build the UI shell for the public Gmail cleanup app so later backend work can plug into real views instead of placeholders.

## Allowed paths

- `apps/web/**`

## Required outputs

- marketing landing page
- signed-in dashboard shell
- left sidebar with `전체 정리`
- sender-group review layout with checkbox selection
- preview modal shell and result panel shell

## Constraints

- use `@cleanmail/contracts` for view models where possible
- do not embed Gmail logic, DB logic, or token handling
- preserve the existing visual direction instead of reverting to template defaults

## Done when

- a reviewer can navigate the app shell and understand the intended flow end-to-end
- fake data can be swapped with real contracts without restructuring the UI tree

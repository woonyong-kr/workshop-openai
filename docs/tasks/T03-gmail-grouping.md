# T03 Gmail Grouping

## Goal

Port the Gmail sender grouping and classification logic from the Python reference into TypeScript library code.

## Allowed paths

- `packages/gmail-core/**`
- `packages/contracts/**` only if a missing shared type blocks you

## Source of truth

- `skills/gmail-mailbox-cleanup/scripts/gmail_cleanup.py`

## Required outputs

- sender parsing and normalization
- domain and local-part heuristics
- classification scoring for newsletter, spam, personal-contact, transactional, social, organization, and unknown
- unsubscribe header parsing for HTTP and `mailto:`
- grouped summary builder from message metadata

## Constraints

- do not call live Gmail or external unsubscribe endpoints in this task
- accept metadata, headers, labels, snippet, and subject as input
- keep exported functions deterministic and easy to test

## Done when

- another agent can call the library with fixture messages and receive stable grouped results
- the public surface is clean enough for `T06` and `T08` to consume directly

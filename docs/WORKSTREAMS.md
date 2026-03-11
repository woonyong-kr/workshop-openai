# Multi-Agent Workstreams

Use these files as the operating set:

- [Task Board](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/TASK_BOARD.md)
- [Agent Messages](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/AGENT_MESSAGES.md)
- [T01 Contracts](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T01-contracts-baseline.md)
- [T02 Web Shell](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T02-web-shell.md)
- [T03 Gmail Grouping](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T03-gmail-grouping.md)
- [T04 Auth Session](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T04-auth-session.md)
- [T05 Data Schema](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T05-data-schema.md)
- [T06 Scan Preview Execute](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T06-scan-preview-execute.md)
- [T07 Review UI](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T07-review-ui.md)
- [T08 API Integration](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T08-api-integration.md)
- [T09 Launch Docs](/Users/woonyong/workspace/Krafton-Jungle/workshop-openai/docs/tasks/T09-launch-docs.md)

## Coordination Rules

- Shared contracts move first through `packages/contracts`.
- Each agent stays inside its allowed paths.
- Any contract change must be reported in the agent handoff.
- `skills/gmail-mailbox-cleanup` is reference material only.

## Recommended First Wave

1. Run `T01-contracts-baseline` as a short shared pass.
2. Start `T02-web-shell`, `T03-gmail-grouping`, `T04-auth-session`, and `T05-data-schema` in parallel.
3. Start `T06`, `T07`, `T08`, and `T09` only after their dependencies are satisfied on the task board.

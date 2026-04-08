---
name: jora
description: Use the jora CLI to interact with Jira — search issues, log work, update tickets, and manage worklogs. Invoke when the user mentions Jira tickets, issue keys (e.g. PROJ-123), time tracking, worklogs, or any Jira workflow.
---

Use the `jora` CLI for all Jira interactions. Never open a browser or use the Jira web UI.

## Key commands

| Command | What it does |
|---|---|
| `jora search "<JQL>" --json` | Flexible JQL search |
| `jora issue get <KEY> --json` | Full details for one issue |
| `jora issue list --project X --assignee me --json` | Filtered issue list |
| `jora issue create --project X --summary "..." --type Bug --json` | Create an issue |
| `jora issue update <KEY> --estimate 4h --json` | Update fields |
| `jora issue comment <KEY> --json` | List comments |
| `jora issue comment <KEY> --body "..." --json` | Add a comment |
| `jora worklog add <KEY> --time "2h 30m" --comment "..." --json` | Log work |
| `jora worklog list <KEY> --json` | List worklogs |
| `jora batch find-incomplete --project X --assignee me --json` | Issues missing estimates |
| `jora batch update --project X --set-estimate 4h --json` | Bulk set estimates |
| `jora issue link-types --json` | Available link type names |
| `jora issue link <KEY> <TYPE> <TARGET> --json` | Link two issues |
| `jora issue links <KEY> --json` | List all links on an issue |

## Rules

- Always use `--json` so output is machine-readable.
- Run `jora context --json` at session start to refresh command and schema details.
- Time formats: `2h 30m`, `90m`, `1.5h`.
- `--started` accepts `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`.
- Exit codes: 0 success · 1 auth/API error · 2 not found · 3 permission denied · 4 invalid input.
- Errors in `--json` mode come as `{"error": "...", "code": "..."}` on stdout.

## Workflow pattern

1. Search or list to get issue keys.
2. Fetch full details with `jora issue get <KEY> --json` before any update.
3. Apply changes; confirm with the user before destructive or bulk operations.

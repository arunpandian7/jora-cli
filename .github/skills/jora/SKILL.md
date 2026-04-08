---
name: jora
description: "Use the jora CLI for Jira interactions — search issues, log work, update tickets, create issues, and manage worklogs. Activate when the user mentions Jira, issue keys (e.g. PROJ-123), sprints, worklogs, or time tracking."
allowed-tools: shell
---

Use the `jora` CLI for all Jira interactions. Do not open a browser or call the Jira REST API directly.

## Key commands

```bash
# Search with JQL
jora search "assignee = currentUser() AND status != Done" --json

# Single issue
jora issue get PROJ-123 --json

# List with filters
jora issue list --project PROJ --assignee me --status "In Progress" --json

# Create
jora issue create --project PROJ --summary "Fix timeout" --type Bug --estimate 2h --json

# Update
jora issue update PROJ-123 --estimate 4h --json

# Comments — list or add
jora issue comment PROJ-123 --json
jora issue comment PROJ-123 --body "Root cause found." --json

# Log work
jora worklog add PROJ-123 --time "2h 30m" --comment "Reviewed PR" --json

# Worklogs
jora worklog list PROJ-123 --json

# Batch: find missing estimates / bulk-set estimates
jora batch find-incomplete --project PROJ --assignee me --json
jora batch update --project PROJ --set-estimate 4h --json

# Links: list types, create a link, list links on an issue
jora issue link-types --json
jora issue link PROJ-123 "Blocks" PROJ-456 --json
jora issue links PROJ-123 --json
```

## Rules

- Always pass `--json` for machine-readable output.
- Run `jora context --json` at session start to get the full command reference and output schemas.
- Time formats: `2h 30m`, `90m`, `1.5h`.
- `--started` accepts `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`.
- Exit codes: 0 success · 1 auth/API error · 2 not found · 3 permission denied · 4 invalid input.
- Errors in `--json` mode: `{"error": "...", "code": "..."}` on stdout.

## Workflow pattern

1. Search or list to get issue keys.
2. Fetch full details with `jora issue get <KEY> --json` before any update.
3. Apply changes; confirm with the user before destructive or bulk operations.

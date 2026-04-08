## Jira — use the jora CLI

When the user wants to interact with Jira (search issues, log time, update tickets, create issues, read comments), use the `jora` CLI. Do not open a browser or use the Jira REST API directly.

### Core commands

```bash
# Search
jora search "assignee = currentUser() AND status != Done" --json

# Single issue
jora issue get PROJ-123 --json

# List with filters
jora issue list --project PROJ --assignee me --status "In Progress" --json

# Create
jora issue create --project PROJ --summary "Fix timeout" --type Bug --estimate 2h --json

# Update
jora issue update PROJ-123 --estimate 4h --json

# Comments (list / add)
jora issue comment PROJ-123 --json
jora issue comment PROJ-123 --body "Root cause found." --json

# Log work
jora worklog add PROJ-123 --time "2h 30m" --comment "Reviewed PR" --json

# Batch
jora batch find-incomplete --project PROJ --assignee me --json
jora batch update --project PROJ --set-estimate 4h --json

# Links
jora issue link-types --json
jora issue link PROJ-123 "Blocks" PROJ-456 --json
jora issue links PROJ-123 --json
```

### Tips

- Always pass `--json` for machine-readable output.
- Time formats: `2h 30m`, `90m`, `1.5h`.
- Run `jora context --json` to get the full command reference and output schemas.
- Exit codes: 0 success, 1 auth error, 2 not found, 3 permission denied, 4 invalid input.

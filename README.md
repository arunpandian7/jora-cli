# Jora

A CLI tool for managing Jira tickets, designed for both human use and LLM agent workflows.

## Installation

```bash
uv tool install .
```

This installs `jora` to `~/.local/bin/jora`.

## Setup

```bash
jora config init
```

Configuration is stored at `~/.config/jora/config.toml`. Multiple Jira instance profiles are supported.

### Non-interactive setup

```bash
jora config add-profile work \
  --server https://your-jira.example.com \
  --token YOUR_TOKEN \
  --default-project MYPROJ \
  --timezone Asia/Tokyo
```

## Commands

### Issues

```bash
jora issue get PROJ-123
jora issue list --project PROJ --assignee me --status "In Progress"
jora issue create --project PROJ --summary "Fix login timeout" --type Bug --estimate "2h"
jora issue update PROJ-123 --estimate "4h" --assignee me
jora issue comment PROJ-123 --body "Investigated, root cause found."
jora issue comment PROJ-123        # list existing comments
```

### Work logging

```bash
jora worklog add PROJ-123 --time "2h 30m" --comment "Implemented fix"
jora worklog add PROJ-123 --time "1h" --started "2026-04-07T14:00" --timezone Asia/Tokyo
jora worklog list PROJ-123
```

### Search

```bash
jora search "project = PROJ AND sprint in openSprints() AND assignee = currentUser()"
jora search "status = 'In Progress'" --json --max 20
```

### Batch operations

```bash
jora batch find-incomplete --project PROJ --assignee me
jora batch update --project PROJ --set-estimate "4h"   # non-interactive
jora batch update --project PROJ                        # interactive (requires TTY)
```

### Configuration

```bash
jora config show
jora config add-profile staging --server https://staging-jira.example.com --token TOKEN
jora config set-default staging
```

## LLM Agent Usage

See **[PROMPTS.md](PROMPTS.md)** for a library of copy-paste prompts covering common workflows:
filling estimates and worklogs for a release, summarising ticket discussions, posting
LLM-generated summaries as comments, creating tickets from meeting notes, triaging backlogs,
and more.

To give an agent full awareness of Jora's commands and output schemas, run:

```bash
jora context          # paste into your system prompt (Markdown)
jora context --json   # structured JSON for programmatic injection
```

All read commands support `--json` for machine-parseable output. Use `--compact` on list/search commands to reduce token usage.

```bash
# Get structured ticket data
jora issue get PROJ-123 --json

# Search with JQL, pipe to jq
jora search "assignee = currentUser() AND status != Done" --json | jq '.[].key'

# Find incomplete tickets
jora batch find-incomplete --project PROJ --assignee me --json

# Non-interactive bulk update
jora batch update --project PROJ --fix-version "v2.0" --set-estimate "4h"
```

**Exit codes:** 0 = success, 1 = error, 2 = not found, 3 = permission denied, 4 = invalid input.

## Time formats

Accepted: `2h 30m`, `2h30m`, `90m`, `1.5h`, `4h`.

## Profile switching

```bash
jora --profile staging issue list --project PROJ
JORA_PROFILE=staging jora issue list
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `JORA_TOKEN` | API token (overrides config/keyring) |
| `JORA_SERVER` | Server URL override |
| `JORA_PROFILE` | Active profile name |
| `JORA_DEFAULT_PROJECT` | Default project for `issue list` |
| `JIRA_API_TOKEN` | Legacy token variable (still supported) |

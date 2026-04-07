"""jora context — agent-optimised reference for the CLI."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# ---------------------------------------------------------------------------
# Reference data — update this when commands or schemas change
# ---------------------------------------------------------------------------

_COMMANDS = [
    {
        "name": "search <JQL>",
        "flags": "--max INT  --json  --compact",
        "desc": "Raw JQL search. Most flexible command for agents.",
        "example": 'jora search "project = PROJ AND assignee = currentUser()" --json',
    },
    {
        "name": "issue get <KEY>",
        "flags": "--json",
        "desc": "Full details for one issue.",
        "example": "jora issue get PROJ-123 --json",
    },
    {
        "name": "issue list",
        "flags": "--project  --fix-version  --assignee  --status  --jql  --max INT  --json  --compact",
        "desc": "List issues. All filters combine with AND. --jql appends an extra clause.",
        "example": 'jora issue list --project PROJ --assignee me --status "In Progress" --json',
    },
    {
        "name": "issue create",
        "flags": "--project*  --summary*  --description  --type  --assignee  --fix-version  --estimate  --json",
        "desc": "Create an issue. Flags marked * are required.",
        "example": 'jora issue create --project PROJ --summary "Fix timeout" --type Bug --estimate "2h" --json',
    },
    {
        "name": "issue update <KEY>",
        "flags": "--summary  --description  --assignee  --fix-version  --estimate  --json",
        "desc": "Update any combination of fields.",
        "example": "jora issue update PROJ-123 --estimate 4h --json",
    },
    {
        "name": "issue comment <KEY>",
        "flags": "--body  --json",
        "desc": "Omit --body to list comments; provide --body to add one.",
        "example": 'jora issue comment PROJ-123 --body "Root cause identified." --json',
    },
    {
        "name": "worklog add <KEY>",
        "flags": "--time*  --comment  --started DATETIME  --timezone TZ  --json",
        "desc": "Log work. --started accepts YYYY-MM-DD or YYYY-MM-DDTHH:MM.",
        "example": 'jora worklog add PROJ-123 --time "2h 30m" --comment "Reviewed PR" --json',
    },
    {
        "name": "worklog list <KEY>",
        "flags": "--json",
        "desc": "List all worklogs for an issue.",
        "example": "jora worklog list PROJ-123 --json",
    },
    {
        "name": "batch find-incomplete",
        "flags": "--project  --fix-version  --assignee  --max INT  --json",
        "desc": "Issues missing original estimates or with remaining time > 0.",
        "example": "jora batch find-incomplete --project PROJ --assignee me --json",
    },
    {
        "name": "batch update",
        "flags": "--project  --fix-version  --assignee  --set-estimate  --json",
        "desc": "Non-interactive when --set-estimate given; requires TTY otherwise.",
        "example": "jora batch update --project PROJ --set-estimate 4h --json",
    },
]

_SCHEMAS = {
    "Issue": {
        "key": "PROJ-123",
        "summary": "Fix login timeout",
        "status": "In Progress",
        "issue_type": "Bug",
        "priority": "High",
        "assignee": {"account_id": "abc123", "display_name": "Alice", "email_address": "alice@example.com"},
        "reporter": {"account_id": "def456", "display_name": "Bob", "email_address": None},
        "fix_versions": ["v2.1.0"],
        "labels": ["backend"],
        "description": "Login times out after 30 seconds under load.",
        "time_tracking": {
            "original_estimate": "4h 0m",
            "original_estimate_seconds": 14400,
            "remaining_estimate": "2h 0m",
            "remaining_estimate_seconds": 7200,
            "time_spent": "2h 0m",
            "time_spent_seconds": 7200,
        },
        "created": "2026-01-15T09:00:00+09:00",
        "updated": "2026-04-07T14:30:00+09:00",
        "url": "https://jira.example.com/browse/PROJ-123",
    },
    "Worklog": {
        "id": "10042",
        "author": {"account_id": "abc123", "display_name": "Alice", "email_address": None},
        "time_spent": "2h",
        "time_spent_seconds": 7200,
        "started": "2026-04-07T14:00:00+00:00",
        "comment": "Reviewed PR and fixed test failures",
        "created": "2026-04-07T14:05:00+00:00",
        "updated": "2026-04-07T14:05:00+00:00",
    },
    "OperationResult": {
        "success": True,
        "issue_key": "PROJ-123",
        "message": "Updated PROJ-123",
        "data": None,
    },
    "ErrorResult": {
        "error": "Issue 'PROJ-999' not found.",
        "code": "NOT_FOUND",
        "details": None,
    },
}

_EXIT_CODES = {
    "0": "success",
    "1": "auth / API error",
    "2": "not found",
    "3": "permission denied",
    "4": "invalid input / not a TTY",
}

_TIME_FORMATS = ["2h 30m", "2h30m", "90m", "1.5h", "4h"]

_AGENT_PATTERNS = [
    ("Scan open tickets for yourself",
     'jora search "assignee = currentUser() AND status != Done" --json --compact'),
    ("Find tickets missing estimates",
     "jora batch find-incomplete --project PROJ --assignee me --json"),
    ("Read a ticket before updating it",
     "jora issue get PROJ-123 --json"),
    ("Log work with a specific start time",
     "jora worklog add PROJ-123 --time 2h --comment 'Pair programming' --started 2026-04-07T14:00 --json"),
    ("Bulk-set estimates after planning",
     "jora batch update --project PROJ --fix-version v2.1 --set-estimate 4h --json"),
    ("Create a ticket and capture the new key",
     "jora issue create --project PROJ --summary 'Investigate memory leak' --type Task --estimate 3h --json | jq -r '.issue_key'"),
]


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _build_markdown() -> str:
    lines: list[str] = []

    lines.append("# Jora CLI — Agent Reference\n")
    lines.append("Global flags available on every command: `--profile NAME` (selects config profile)\n")

    lines.append("## Commands\n")
    for cmd in _COMMANDS:
        lines.append(f"### `jora {cmd['name']}`")
        lines.append(f"{cmd['desc']}")
        lines.append(f"Flags: `{cmd['flags']}`")
        lines.append(f"```\n{cmd['example']}\n```\n")

    lines.append("## Time formats\n")
    lines.append(", ".join(f"`{t}`" for t in _TIME_FORMATS) + "\n")

    lines.append("## Exit codes\n")
    for code, meaning in _EXIT_CODES.items():
        lines.append(f"- `{code}` — {meaning}")
    lines.append("")

    lines.append("## JSON output — error format\n")
    lines.append("All commands in `--json` mode emit errors as JSON to stdout (plus human text to stderr):\n")
    lines.append(f"```json\n{json.dumps(_SCHEMAS['ErrorResult'], indent=2)}\n```\n")

    lines.append("## JSON output — Issue schema\n")
    lines.append(f"```json\n{json.dumps(_SCHEMAS['Issue'], indent=2)}\n```\n")

    lines.append("## JSON output — write commands (OperationResult)\n")
    lines.append(f"```json\n{json.dumps(_SCHEMAS['OperationResult'], indent=2)}\n```\n")

    lines.append("## Agent usage patterns\n")
    for desc, cmd in _AGENT_PATTERNS:
        lines.append(f"**{desc}**")
        lines.append(f"```\n{cmd}\n```\n")

    return "\n".join(lines)


def _build_json() -> str:
    data = {
        "commands": _COMMANDS,
        "time_formats": _TIME_FORMATS,
        "exit_codes": _EXIT_CODES,
        "output_schemas": _SCHEMAS,
        "agent_patterns": [
            {"description": desc, "command": cmd} for desc, cmd in _AGENT_PATTERNS
        ],
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

def context_cmd(
    as_json: bool = typer.Option(False, "--json", help="Emit structured JSON instead of Markdown."),
) -> None:
    """Print a compact reference for using Jora as an LLM agent tool.

    Pipe the output into your agent's system prompt to give it full
    awareness of available commands, flag names, output schemas, and
    common usage patterns — without the verbosity of --help.

    Examples:
      jora context                  # Markdown (readable, pasteable into system prompt)
      jora context --json           # Structured JSON (for programmatic injection)
    """
    if as_json:
        print(_build_json())
    else:
        console.print(Markdown(_build_markdown()))

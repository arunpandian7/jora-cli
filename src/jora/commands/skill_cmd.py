"""jora skill — install AI assistant skill/context files for Jora."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Manage AI assistant skill files for Jora.")
console = Console()


class AITool(str, Enum):
    claude = "claude"
    copilot = "copilot"
    cursor = "cursor"


class Scope(str, Enum):
    workspace = "workspace"
    home = "home"


# ---------------------------------------------------------------------------
# Skill file content
# ---------------------------------------------------------------------------

# Claude Code: .claude/skills/jora.md  or  ~/.claude/skills/jora.md
_CONTENT_CLAUDE = """\
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
"""

# GitHub Copilot: .github/skills/jora/SKILL.md  or  ~/.copilot/skills/jora/SKILL.md
_CONTENT_COPILOT = """\
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
"""

# Cursor: .cursor/rules/jora.mdc
_CONTENT_CURSOR = """\
---
description: Use the jora CLI for Jira — search issues, log work, update tickets, and manage worklogs.
globs:
alwaysApply: false
---

Use the `jora` CLI for all Jira interactions. Do not open a browser or use the Jira REST API directly.

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

# Batch: find missing estimates / bulk-set estimates
jora batch find-incomplete --project PROJ --assignee me --json
jora batch update --project PROJ --set-estimate 4h --json
```

## Rules

- Always use `--json` for structured output.
- Run `jora context --json` at session start for the full command reference and output schemas.
- Time formats: `2h 30m`, `90m`, `1.5h`.
- `--started` accepts `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`.
- Exit codes: 0 success · 1 auth/API error · 2 not found · 3 permission denied · 4 invalid input.
- Errors in `--json` mode: `{"error": "...", "code": "..."}` on stdout.
"""


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_TOOL_LABELS = {
    AITool.claude: "Claude Code",
    AITool.copilot: "GitHub Copilot",
    AITool.cursor: "Cursor",
}

_SCOPE_LABELS = {
    Scope.workspace: "current workspace",
    Scope.home: "home directory (~)",
}

# Claude: ~/.claude/skills/  |  Copilot: ~/.copilot/skills/  |  Cursor: workspace only
_HOME_PATHS = {
    AITool.claude: Path.home() / ".claude" / "skills" / "jora.md",
    AITool.copilot: Path.home() / ".copilot" / "skills" / "jora" / "SKILL.md",
}


def _resolve_path(tool: AITool, scope: Scope, cwd: Path) -> Path:
    if scope == Scope.home:
        if tool not in _HOME_PATHS:
            raise ValueError(f"{_TOOL_LABELS[tool]} does not support home-level skill files.")
        return _HOME_PATHS[tool]
    # workspace
    if tool == AITool.claude:
        return cwd / ".claude" / "skills" / "jora.md"
    if tool == AITool.copilot:
        return cwd / ".github" / "skills" / "jora" / "SKILL.md"
    if tool == AITool.cursor:
        return cwd / ".cursor" / "rules" / "jora.mdc"
    raise ValueError(f"Unknown tool: {tool}")  # unreachable


def _get_content(tool: AITool) -> str:
    if tool == AITool.claude:
        return _CONTENT_CLAUDE
    if tool == AITool.copilot:
        return _CONTENT_COPILOT
    return _CONTENT_CURSOR


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

@app.command("install")
def skill_install() -> None:
    """Interactively create and install a Jora skill file for an AI coding assistant.

    Supports Claude Code, GitHub Copilot, and Cursor.  You will be asked where
    to install (workspace or home) and which assistant to target.

    Examples:
      jora skill install
    """
    console.print("[bold]Jora Skill Installer[/bold]\n")

    # --- Select AI tool ---
    console.print("Which AI coding assistant do you use?")
    console.print("  [cyan]1[/cyan]  Claude Code")
    console.print("  [cyan]2[/cyan]  GitHub Copilot")
    console.print("  [cyan]3[/cyan]  Cursor")
    tool_choice = typer.prompt("\nEnter number", default="1")
    tool_map = {"1": AITool.claude, "2": AITool.copilot, "3": AITool.cursor}
    if tool_choice not in tool_map:
        console.print(f"[red]Invalid choice '{tool_choice}'. Pick 1, 2, or 3.[/red]")
        raise typer.Exit(code=4)
    tool = tool_map[tool_choice]

    # --- Select scope ---
    supports_home = tool in _HOME_PATHS
    if supports_home:
        home_hint = str(_HOME_PATHS[tool])
        console.print("\nInstall for:")
        console.print(f"  [cyan]1[/cyan]  This workspace only")
        console.print(f"  [cyan]2[/cyan]  Home (all projects)  ({home_hint})")
        scope_choice = typer.prompt("Enter number", default="1")
        if scope_choice == "1":
            scope = Scope.workspace
        elif scope_choice == "2":
            scope = Scope.home
        else:
            console.print(f"[red]Invalid choice '{scope_choice}'. Pick 1 or 2.[/red]")
            raise typer.Exit(code=4)
    else:
        scope = Scope.workspace
        console.print(f"\n[dim]{_TOOL_LABELS[tool]} only supports workspace-level files.[/dim]")

    # --- Resolve destination path ---
    cwd = Path(os.getcwd())
    try:
        dest = _resolve_path(tool, scope, cwd)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=4)

    content = _get_content(tool)

    # --- Handle existing file ---
    if dest.exists():
        console.print(f"\n[yellow]File already exists:[/yellow] {dest}")
        action = typer.prompt("  [o]verwrite / [c]ancel", default="o").lower()
        if action == "c":
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit()
        elif action != "o":
            console.print("[red]Unknown action. Cancelled.[/red]")
            raise typer.Exit(code=4)

    # --- Write ---
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)

    tool_label = _TOOL_LABELS[tool]
    scope_label = _SCOPE_LABELS[scope]
    console.print(f"\n[bold green]Installed![/bold green] {tool_label} skill file written to:")
    console.print(f"  [cyan]{dest}[/cyan]")
    console.print(f"\nScope: {scope_label}")

    if scope == Scope.home:
        console.print(f"\n[dim]{tool_label} will load this skill automatically in all projects.[/dim]")
    else:
        console.print(f"\n[dim]Commit [cyan]{dest.relative_to(cwd)}[/cyan] to share with your team.[/dim]")

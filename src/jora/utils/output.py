"""Rich tables and JSON output helpers. All commands use these for dual human/machine output."""

from __future__ import annotations

import json
import sys
from typing import Any, List, Union

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..core.models import Comment, ErrorResult, Issue, OperationResult, Worklog

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def output_json(data: Any) -> None:
    """Serialize to JSON and print to stdout. Works with Pydantic models and lists."""
    if isinstance(data, BaseModel):
        print(data.model_dump_json(indent=2))
    elif isinstance(data, list):
        if data and isinstance(data[0], BaseModel):
            print(json.dumps([item.model_dump(mode="json") for item in data], indent=2))
        else:
            print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(data, indent=2, default=str))


def output_error(
    error: str,
    code: str = "ERROR",
    json_mode: bool = False,
    details: str | None = None,
) -> None:
    """Print error. In JSON mode, outputs JSON to stdout AND human text to stderr."""
    result = ErrorResult(error=error, code=code, details=details)
    if json_mode:
        output_json(result)
    err_console.print(f"[bold red]Error[/bold red] [{code}]: {error}", highlight=False)
    if details:
        err_console.print(f"[dim]{details}[/dim]")


def output_success(
    result: OperationResult,
    json_mode: bool = False,
) -> None:
    """Print success result. JSON mode outputs the full OperationResult."""
    if json_mode:
        output_json(result)
    else:
        console.print(f"[bold green]OK[/bold green] {result.message}")


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def issues_table(issues: List[Issue], compact: bool = False) -> Table:
    """Build a Rich table for a list of issues."""
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("Key", style="bold", min_width=10)
    table.add_column("Summary", max_width=60 if not compact else 40)
    table.add_column("Status", min_width=10)
    if not compact:
        table.add_column("Assignee", min_width=15)
        table.add_column("Orig Est", min_width=8)
        table.add_column("Spent", min_width=8)
        table.add_column("Remaining", min_width=8)

    for issue in issues:
        assignee = issue.assignee.display_name if issue.assignee else "Unassigned"
        tt = issue.time_tracking
        summary = issue.summary[:57] + "..." if len(issue.summary) > 60 else issue.summary
        if compact:
            table.add_row(issue.key, summary, issue.status)
        else:
            table.add_row(
                issue.key,
                summary,
                issue.status,
                assignee,
                tt.original_estimate or "Not set",
                tt.time_spent or "Not set",
                tt.remaining_estimate or "Not set",
            )
    return table


def issue_detail_panel(issue: Issue) -> None:
    """Print a detailed panel for a single issue."""
    tt = issue.time_tracking
    assignee = issue.assignee.display_name if issue.assignee else "Unassigned"
    reporter = issue.reporter.display_name if issue.reporter else "Unknown"
    fix_versions = ", ".join(issue.fix_versions) if issue.fix_versions else "None"
    labels = ", ".join(issue.labels) if issue.labels else "None"
    desc = ""
    if issue.description:
        desc = issue.description[:400] + "..." if len(issue.description) > 400 else issue.description
        desc = f"\n[dim]{desc}[/dim]"

    content = (
        f"[bold]{issue.summary}[/bold]\n"
        f"\n"
        f"[cyan]Status:[/cyan]       {issue.status}\n"
        f"[cyan]Type:[/cyan]         {issue.issue_type}\n"
        f"[cyan]Priority:[/cyan]     {issue.priority or 'Not set'}\n"
        f"[cyan]Assignee:[/cyan]     {assignee}\n"
        f"[cyan]Reporter:[/cyan]     {reporter}\n"
        f"[cyan]Fix Versions:[/cyan] {fix_versions}\n"
        f"[cyan]Labels:[/cyan]       {labels}\n"
        f"\n"
        f"[cyan]Original Est:[/cyan] {tt.original_estimate or 'Not set'}\n"
        f"[cyan]Time Spent:[/cyan]   {tt.time_spent or 'Not set'}\n"
        f"[cyan]Remaining:[/cyan]    {tt.remaining_estimate or 'Not set'}\n"
        f"\n"
        f"[cyan]Created:[/cyan]      {issue.created}\n"
        f"[cyan]Updated:[/cyan]      {issue.updated}\n"
        f"[cyan]URL:[/cyan]          {issue.url}"
        f"{desc}"
    )

    console.print(Panel(content, title=f"[bold magenta]{issue.key}[/bold magenta]", expand=False))


def print_issues(issues: List[Issue], json_mode: bool = False, compact: bool = False) -> None:
    """Top-level: print issues as table or JSON."""
    if json_mode:
        output_json(issues)
    else:
        if not issues:
            console.print("[yellow]No issues found.[/yellow]")
            return
        table = issues_table(issues, compact=compact)
        console.print(table)
        console.print(f"[dim]{len(issues)} issue(s)[/dim]")


# ---------------------------------------------------------------------------
# Worklogs
# ---------------------------------------------------------------------------

def worklogs_table(worklogs: List[Worklog]) -> Table:
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("ID", min_width=8)
    table.add_column("Author", min_width=15)
    table.add_column("Time Spent", min_width=10)
    table.add_column("Started")
    table.add_column("Comment")

    for wl in worklogs:
        comment = (wl.comment or "")[:50]
        table.add_row(
            wl.id,
            wl.author.display_name,
            wl.time_spent,
            str(wl.started)[:16],
            comment,
        )
    return table


def print_worklogs(worklogs: List[Worklog], json_mode: bool = False) -> None:
    if json_mode:
        output_json(worklogs)
    else:
        if not worklogs:
            console.print("[yellow]No worklogs found.[/yellow]")
            return
        console.print(worklogs_table(worklogs))


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def print_comments(comments: List[Comment], json_mode: bool = False) -> None:
    if json_mode:
        output_json(comments)
    else:
        if not comments:
            console.print("[yellow]No comments found.[/yellow]")
            return
        for c in comments:
            console.print(Panel(
                f"[dim]{c.body}[/dim]",
                title=f"[bold]{c.author.display_name}[/bold] — {str(c.created)[:16]}",
                expand=False,
            ))

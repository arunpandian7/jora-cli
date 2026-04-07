"""jora issue subcommands: get, list, create, update, comment."""

from __future__ import annotations

from typing import Optional

import typer

from . import get_client
from ..core.client import (
    InvalidInputError,
    JoraError,
    NotFoundError,
)
from ..utils.output import (
    console,
    issue_detail_panel,
    output_error,
    output_json,
    output_success,
    print_comments,
    print_issues,
)

app = typer.Typer(help="Read, create, and update Jira issues.")


@app.command("get")
def issue_get(
    ctx: typer.Context,
    key: str = typer.Argument(help="Issue key, e.g. ARTS-3183"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get full details for a single issue."""
    client = get_client(ctx)
    try:
        issue = client.get_issue(key)
        if as_json:
            output_json(issue)
        else:
            issue_detail_panel(issue)
    except NotFoundError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=2)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("list")
def issue_list(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(
        None, "--project", "-p", envvar="JORA_DEFAULT_PROJECT", help="Project key"
    ),
    fix_version: Optional[str] = typer.Option(None, "--fix-version", "-r", help="Fix version / release"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee (use 'me' for yourself)"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Status name"),
    jql: Optional[str] = typer.Option(None, "--jql", help="Additional JQL clause appended with AND"),
    max_results: int = typer.Option(50, "--max", "-n", help="Maximum number of results"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
    compact: bool = typer.Option(False, "--compact", help="Fewer columns (better for LLM token efficiency)"),
) -> None:
    """List issues with optional filters. All filters combine with AND."""
    client = get_client(ctx)
    try:
        query = client.build_filter_jql(
            project=project or client.default_project,
            fix_version=fix_version,
            assignee=assignee,
            status=status,
            extra_jql=jql,
        )
        issues = client.search_issues(query, max_results=max_results)
        print_issues(issues, json_mode=as_json, compact=compact)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("create")
def issue_create(
    ctx: typer.Context,
    project: str = typer.Option(..., "--project", "-p", help="Project key"),
    summary: str = typer.Option(..., "--summary", "-s", help="Issue summary / title"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    issue_type: str = typer.Option("Task", "--type", "-t", help="Issue type, e.g. Task, Bug, Story"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee (use 'me' for yourself)"),
    fix_version: Optional[str] = typer.Option(None, "--fix-version", "-r"),
    original_estimate: Optional[str] = typer.Option(None, "--estimate", "-e", help="e.g. '2h 30m'"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Create a new issue. All fields provided via flags — no prompts."""
    client = get_client(ctx)
    try:
        result = client.create_issue(
            project=project,
            summary=summary,
            description=description,
            issue_type=issue_type,
            assignee=assignee,
            fix_version=fix_version,
            original_estimate=original_estimate,
        )
        output_success(result, json_mode=as_json)
        if not as_json and result.data:
            console.print(f"  URL: [link={result.data['url']}]{result.data['url']}[/link]")
    except InvalidInputError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=4)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("update")
def issue_update(
    ctx: typer.Context,
    key: str = typer.Argument(help="Issue key"),
    summary: Optional[str] = typer.Option(None, "--summary"),
    description: Optional[str] = typer.Option(None, "--description"),
    assignee: Optional[str] = typer.Option(None, "--assignee"),
    fix_version: Optional[str] = typer.Option(None, "--fix-version"),
    original_estimate: Optional[str] = typer.Option(None, "--estimate", "-e", help="e.g. '4h'"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Update fields on an existing issue."""
    if not any([summary, description, assignee, fix_version, original_estimate]):
        console.print("[yellow]Nothing to update. Provide at least one field flag.[/yellow]")
        raise typer.Exit(code=4)

    client = get_client(ctx)
    try:
        result = client.update_issue(
            key=key,
            summary=summary,
            description=description,
            assignee=assignee,
            fix_version=fix_version,
            original_estimate=original_estimate,
        )
        output_success(result, json_mode=as_json)
    except NotFoundError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=2)
    except InvalidInputError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=4)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("comment")
def issue_comment(
    ctx: typer.Context,
    key: str = typer.Argument(help="Issue key"),
    body: Optional[str] = typer.Option(
        None, "--body", "-b", help="Comment text. Omit to list existing comments."
    ),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Add a comment or list existing comments on an issue.

    Pass --body to add a new comment; omit it to list all comments.
    """
    client = get_client(ctx)
    try:
        if body:
            result = client.add_comment(key, body)
            output_success(result, json_mode=as_json)
        else:
            comments = client.list_comments(key)
            print_comments(comments, json_mode=as_json)
    except NotFoundError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=2)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)

"""jora search command — raw JQL search."""

from __future__ import annotations

import typer

from . import get_client
from ..core.client import InvalidInputError, JoraError
from ..utils.output import output_error, print_issues

app = typer.Typer()


def search_cmd(
    ctx: typer.Context,
    jql: str = typer.Argument(help='JQL query string, e.g. "project = ARTS AND assignee = currentUser()"'),
    max_results: int = typer.Option(50, "--max", "-n", help="Maximum results"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
    compact: bool = typer.Option(False, "--compact", help="Fewer columns (LLM-efficient)"),
) -> None:
    """Execute a raw JQL search query.

    This is the most powerful command for LLM agents — construct any JQL and get
    structured JSON output.

    Examples:
      jora search "project = ARTS AND sprint in openSprints()" --json
      jora search "assignee = currentUser() AND status != Done" --compact
    """
    client = get_client(ctx)
    try:
        issues = client.search_issues(jql, max_results=max_results)
        print_issues(issues, json_mode=as_json, compact=compact)
    except InvalidInputError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=4)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)

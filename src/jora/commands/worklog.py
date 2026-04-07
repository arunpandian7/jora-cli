"""jora worklog subcommands: add, list."""

from __future__ import annotations

from typing import Optional

import typer

from . import get_client
from ..core.client import InvalidInputError, JoraError, NotFoundError
from ..utils.output import output_error, output_success, print_worklogs

app = typer.Typer(help="Log and view work on Jira issues.")


@app.command("add")
def worklog_add(
    ctx: typer.Context,
    key: str = typer.Argument(help="Issue key, e.g. ARTS-3183"),
    time_spent: str = typer.Option(..., "--time", "-t", help="Time spent, e.g. '2h 30m', '90m', '1.5h'"),
    comment: Optional[str] = typer.Option(None, "--comment", "-c", help="Work description"),
    started: Optional[str] = typer.Option(
        None,
        "--started",
        "-s",
        help="When work started: ISO date (2026-04-07) or datetime (2026-04-07T14:30)",
    ),
    timezone: Optional[str] = typer.Option(
        None, "--timezone", "-z", help="Timezone override, e.g. 'Asia/Tokyo'. Defaults to profile timezone."
    ),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Log work on an issue. Fully non-interactive."""
    client = get_client(ctx)
    try:
        result = client.add_worklog(
            key=key,
            time_spent=time_spent,
            comment=comment,
            started=started,
            timezone=timezone,
        )
        output_success(result, json_mode=as_json)
    except InvalidInputError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=4)
    except NotFoundError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=2)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("list")
def worklog_list(
    ctx: typer.Context,
    key: str = typer.Argument(help="Issue key"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """List all worklogs for an issue."""
    client = get_client(ctx)
    try:
        worklogs = client.list_worklogs(key)
        print_worklogs(worklogs, json_mode=as_json)
    except NotFoundError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=2)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)

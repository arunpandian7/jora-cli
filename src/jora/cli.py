"""Main Typer application entry point."""

from __future__ import annotations

from typing import Optional

import typer

from . import __version__
from .commands import batch, config_cmd, context_cmd, issue, search, worklog

app = typer.Typer(
    name="jora",
    help="[bold]Jora[/bold] — LLM-friendly Jira CLI for humans and agents.",
    no_args_is_help=True,
    invoke_without_command=True,
    add_completion=True,
    rich_markup_mode="rich",
)

# Register sub-applications
app.add_typer(issue.app, name="issue")
app.add_typer(worklog.app, name="worklog")
app.add_typer(config_cmd.app, name="config")
app.add_typer(batch.app, name="batch")

# Register standalone commands
app.command("search")(search.search_cmd)
app.command("context")(context_cmd.context_cmd)


@app.callback()
def main(
    ctx: typer.Context,
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-P",
        envvar="JORA_PROFILE",
        help="Config profile name (overrides JORA_PROFILE env var).",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Jora — LLM-friendly Jira CLI."""
    if version:
        typer.echo(f"jora {__version__}")
        raise typer.Exit()

    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile

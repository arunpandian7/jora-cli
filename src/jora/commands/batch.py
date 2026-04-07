"""jora batch subcommands: find-incomplete, update."""

from __future__ import annotations

import sys
from typing import Optional

import typer

from . import get_client
from ..core.client import InvalidInputError, JoraError
from ..utils.output import console, issues_table, output_error, output_json, output_success, print_issues

app = typer.Typer(help="Batch operations across multiple Jira issues.")


@app.command("find-incomplete")
def batch_find_incomplete(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project key"),
    fix_version: Optional[str] = typer.Option(None, "--fix-version", "-r", help="Fix version"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee ('me' for yourself)"),
    max_results: int = typer.Option(50, "--max", "-n"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Find tickets missing original estimates or with remaining time.

    LLM agents: pipe this into 'jora issue update' or 'jora worklog add' per ticket.
    """
    client = get_client(ctx)
    try:
        issues = client.find_incomplete_tickets(
            project=project,
            fix_version=fix_version,
            assignee=assignee,
            max_results=max_results,
        )
        print_issues(issues, json_mode=as_json)
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)


@app.command("update")
def batch_update(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(None, "--project", "-p"),
    fix_version: Optional[str] = typer.Option(None, "--fix-version", "-r"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a"),
    max_results: int = typer.Option(50, "--max"),
    set_estimate: Optional[str] = typer.Option(
        None,
        "--set-estimate",
        help="Non-interactive: apply this estimate to ALL found tickets.",
    ),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Batch time tracking update.

    Without --set-estimate: interactive mode (prompts per ticket, requires a TTY).
    With --set-estimate: non-interactive — applies estimate to all matched tickets.

    LLM agents should use --set-estimate, or loop over 'jora issue update <KEY> --estimate'.
    """
    client = get_client(ctx)

    try:
        issues = client.find_incomplete_tickets(
            project=project,
            fix_version=fix_version,
            assignee=assignee,
            max_results=max_results,
        )
    except JoraError as e:
        output_error(e.message, e.code, json_mode=as_json)
        raise typer.Exit(code=1)

    if not issues:
        if as_json:
            output_json({"message": "No incomplete tickets found.", "updated": [], "skipped": []})
        else:
            console.print("[yellow]No incomplete tickets found.[/yellow]")
        return

    # ------------------------------------------------------------------
    # Non-interactive mode: --set-estimate provided
    # ------------------------------------------------------------------
    if set_estimate is not None:
        updated = []
        failed = []
        for issue in issues:
            try:
                result = client.set_original_estimate(issue.key, set_estimate)
                if result.success:
                    updated.append(issue.key)
                else:
                    failed.append({"key": issue.key, "reason": result.message})
            except (InvalidInputError, JoraError) as e:
                failed.append({"key": issue.key, "reason": e.message})

        if as_json:
            output_json({"updated": updated, "failed": failed, "total": len(issues)})
        else:
            console.print(f"[bold green]Updated:[/bold green] {len(updated)} tickets")
            if failed:
                console.print(f"[bold red]Failed:[/bold red] {len(failed)} tickets")
                for f in failed:
                    console.print(f"  [red]{f['key']}:[/red] {f['reason']}")
        return

    # ------------------------------------------------------------------
    # Interactive mode: requires a TTY
    # ------------------------------------------------------------------
    if not sys.stdin.isatty():
        output_error(
            "Interactive batch update requires a TTY. Use --set-estimate for non-interactive mode.",
            code="NOT_A_TTY",
            json_mode=as_json,
        )
        raise typer.Exit(code=4)

    console.print(f"\n[bold]Batch Update — {len(issues)} tickets[/bold]\n")
    console.print(issues_table(issues))
    console.print()

    updated_count = 0
    skipped_count = 0

    for i, issue in enumerate(issues, 1):
        tt = issue.time_tracking
        console.print(f"\n[bold cyan][{i}/{len(issues)}] {issue.key}[/bold cyan] — {issue.summary}")
        console.print(f"  Original Est: {tt.original_estimate or 'Not set'}  "
                      f"Spent: {tt.time_spent or 'Not set'}  "
                      f"Remaining: {tt.remaining_estimate or 'Not set'}")

        console.print("  [1] Set estimate  [2] Log work  [3] Both  [4] Skip  [0] Stop")
        try:
            choice = typer.prompt("  Choice", default="4").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Stopped.[/yellow]")
            break

        if choice == "0":
            console.print("[yellow]Stopped.[/yellow]")
            break

        if choice == "4":
            skipped_count += 1
            continue

        if choice in ("1", "3"):
            estimate_str = typer.prompt(f"  Estimate for {issue.key} (e.g. '4h')").strip()
            if estimate_str and estimate_str.lower() != "skip":
                try:
                    result = client.set_original_estimate(issue.key, estimate_str)
                    if result.success:
                        console.print("  [green]Estimate set.[/green]")
                        updated_count += 1
                    else:
                        console.print(f"  [red]Failed:[/red] {result.message}")
                except JoraError as e:
                    console.print(f"  [red]Error:[/red] {e.message}")

        if choice in ("2", "3"):
            time_str = typer.prompt(f"  Time spent for {issue.key} (e.g. '2h')").strip()
            if time_str and time_str.lower() != "skip":
                comment = typer.prompt("  Work description (optional)", default="").strip()
                started = typer.prompt("  Started (YYYY-MM-DD or YYYY-MM-DDTHH:MM, Enter for now)", default="").strip()
                try:
                    result = client.add_worklog(
                        issue.key,
                        time_str,
                        comment=comment or None,
                        started=started or None,
                    )
                    if result.success:
                        console.print("  [green]Work logged.[/green]")
                        updated_count += 1
                    else:
                        console.print(f"  [red]Failed:[/red] {result.message}")
                except JoraError as e:
                    console.print(f"  [red]Error:[/red] {e.message}")

    console.print(f"\n[bold]Summary:[/bold] updated {updated_count}, skipped {skipped_count} of {len(issues)}")

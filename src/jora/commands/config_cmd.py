"""jora config subcommands."""

from __future__ import annotations

import getpass
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ..core.config import (
    CONFIG_FILE,
    JoraConfig,
    ProfileConfig,
    load_config,
    save_config,
)
from ..utils.output import output_json

app = typer.Typer(help="Manage Jora configuration and profiles.")
console = Console()


@app.command("init")
def config_init() -> None:
    """Interactive wizard to create initial configuration."""
    console.print("[bold]Jora Configuration Setup[/bold]")
    console.print(f"Config will be saved to: [cyan]{CONFIG_FILE}[/cyan]\n")

    config = load_config()

    profile_name = typer.prompt("Profile name", default="default")
    server = typer.prompt("Jira server URL", default="https://your-jira-instance.example.com")
    username = typer.prompt("Jira username / email (optional, press Enter to skip)", default="")
    token = getpass.getpass("Jira Personal Access Token: ")

    use_keyring = False
    try:
        import keyring  # noqa: F401
        use_keyring_answer = typer.confirm("Store token in system keyring? (more secure)", default=True)
        use_keyring = use_keyring_answer
    except ImportError:
        console.print("[dim]keyring not available, storing token in config file.[/dim]")

    default_project = typer.prompt("Default project key (optional, press Enter to skip)", default="")
    default_assignee = typer.prompt("Default assignee ('me' for yourself, optional)", default="")
    timezone = typer.prompt("Your timezone (e.g. Asia/Tokyo, UTC)", default="UTC")

    profile = ProfileConfig(
        server=server.rstrip("/"),
        username=username or None,
        token_source="keyring" if use_keyring else "config",
        token="" if use_keyring else token,
        default_project=default_project or None,
        default_assignee=default_assignee or None,
        timezone=timezone,
    )

    if use_keyring:
        try:
            import keyring
            keyring.set_password("jora", profile_name, token)
            console.print("[green]Token stored in system keyring.[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: keyring storage failed ({e}). Storing in config file.[/yellow]")
            profile = profile.model_copy(update={"token_source": "config", "token": token})

    config.profiles[profile_name] = profile
    if not config.defaults.get("profile"):
        config.defaults["profile"] = profile_name

    save_config(config)
    console.print(f"\n[bold green]Configuration saved![/bold green]")
    console.print(f"Profile '[cyan]{profile_name}[/cyan]' is now your default.")
    console.print(f"\nTest it with: [bold]jora issue list[/bold]")


@app.command("show")
def config_show(
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
    reveal_token: bool = typer.Option(False, "--reveal-token", help="Show token value (be careful!)"),
) -> None:
    """Display current configuration. Token is masked by default."""
    config = load_config()

    if not config.profiles:
        console.print("[yellow]No configuration found. Run 'jora config init' to set up.[/yellow]")
        raise typer.Exit(code=1)

    if as_json:
        data = config.model_dump()
        if not reveal_token:
            for profile_data in data.get("profiles", {}).values():
                if profile_data.get("token"):
                    profile_data["token"] = "***"
        output_json(data)
        return

    console.print(f"[bold]Config file:[/bold] {CONFIG_FILE}")
    console.print(f"[bold]Default profile:[/bold] {config.defaults.get('profile', 'none')}\n")

    for name, profile in config.profiles.items():
        token_display = "***" if not reveal_token else (profile.token or "(from keyring/env)")
        table = Table(box=box.SIMPLE, show_header=False, title=f"Profile: [cyan]{name}[/cyan]")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        table.add_row("Server", profile.server)
        table.add_row("Username", profile.username or "(not set)")
        table.add_row("Token source", profile.token_source)
        table.add_row("Token", token_display)
        table.add_row("Verify SSL", str(profile.verify_ssl))
        table.add_row("Default project", profile.default_project or "(not set)")
        table.add_row("Default assignee", profile.default_assignee or "(not set)")
        table.add_row("Timezone", profile.timezone)
        console.print(table)


@app.command("add-profile")
def config_add_profile(
    name: str = typer.Argument(help="Profile name"),
    server: str = typer.Option(..., "--server", help="Jira server URL"),
    username: Optional[str] = typer.Option(None, "--username"),
    token: Optional[str] = typer.Option(None, "--token", help="API token (use JORA_TOKEN env var for security)"),
    use_keyring: bool = typer.Option(False, "--keyring", help="Store token in system keyring"),
    default_project: Optional[str] = typer.Option(None, "--default-project"),
    default_assignee: Optional[str] = typer.Option(None, "--default-assignee"),
    timezone: str = typer.Option("UTC", "--timezone"),
    verify_ssl: bool = typer.Option(True, "--verify-ssl/--no-verify-ssl"),
) -> None:
    """Add a new Jira profile non-interactively."""
    import os
    resolved_token = token or os.getenv("JORA_TOKEN") or os.getenv("JIRA_API_TOKEN")

    token_source = "config"
    stored_token = resolved_token

    if use_keyring and resolved_token:
        try:
            import keyring
            keyring.set_password("jora", name, resolved_token)
            token_source = "keyring"
            stored_token = ""
            console.print("[green]Token stored in system keyring.[/green]")
        except Exception as e:
            console.print(f"[yellow]Keyring failed ({e}), storing in config file.[/yellow]")

    profile = ProfileConfig(
        server=server.rstrip("/"),
        username=username,
        token_source=token_source,
        token=stored_token,
        verify_ssl=verify_ssl,
        default_project=default_project,
        default_assignee=default_assignee,
        timezone=timezone,
    )

    config = load_config()
    config.profiles[name] = profile
    save_config(config)
    console.print(f"[bold green]Profile '[cyan]{name}[/cyan]' added.[/bold green]")


@app.command("set-default")
def config_set_default(
    name: str = typer.Argument(help="Profile name to set as default"),
) -> None:
    """Set the default profile."""
    config = load_config()
    if name not in config.profiles:
        console.print(f"[red]Profile '{name}' not found.[/red]")
        raise typer.Exit(code=1)
    config.defaults["profile"] = name
    save_config(config)
    console.print(f"[bold green]Default profile set to '[cyan]{name}[/cyan]'.[/bold green]")

"""Shared helpers for command modules."""

from __future__ import annotations

import typer

from ..core.client import AuthError, JoraClient
from ..core.config import ConfigError, get_effective_profile
from ..utils.output import console


def get_client(ctx: typer.Context) -> JoraClient:
    """Resolve the active profile from context and return a connected JoraClient.

    Prints a user-facing error and exits with code 1 on auth or config failure.
    """
    profile_name = ctx.obj.get("profile") if ctx.obj else None
    try:
        profile = get_effective_profile(profile_name)
        return JoraClient(profile, profile_name or "default")
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)
    except AuthError as e:
        console.print(f"[red]Auth error:[/red] {e.message}")
        raise typer.Exit(code=1)

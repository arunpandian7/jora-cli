# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies (syncs venv)
uv sync

# Install as a home-level CLI tool (editable)
uv tool install --editable .

# Run the CLI without installing
uv run jora <command>

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_time_utils.py

# Run a single test by name
uv run pytest tests/ -k "test_parse_time_input"
```

## Architecture

### Request flow

Every CLI invocation follows this path:

1. **`cli.py`** — Typer app root. Global `--profile`/`--version` callback stores the active profile name in `ctx.obj["profile"]`.
2. **`commands/__init__.py`** — `get_client(ctx)` is the shared helper that resolves the profile and constructs a `JoraClient`. All command modules import and call this instead of duplicating connection logic.
3. **`core/config.py`** — `get_effective_profile()` resolves which profile to use (flag → `JORA_PROFILE` env → config file default → env-var fallback). `resolve_token()` finds the token (env var → keyring → config file).
4. **`core/client.py`** — `JoraClient` wraps the `jira-python` SDK. All Jira API calls live here; no `print()` or `input()` calls. Raises typed subclasses of `JoraError` (`AuthError`, `NotFoundError`, `PermissionError`, `JiraAPIError`, `InvalidInputError`).
5. **`core/models.py`** — Pydantic models (`Issue`, `Worklog`, `Comment`, etc.) with factory methods (`Issue.from_jira_issue(raw, server_url)`) that translate raw SDK objects. Module-level `_parse_jira_datetime` and `_extract_jira_user` helpers are shared across all three factory methods.
6. **`utils/output.py`** — Dual output: `--json` → `output_json(pydantic_model)` to stdout; human mode → Rich tables/panels. `output_error()` always writes human text to stderr, and additionally JSON to stdout when in JSON mode so agents always get parseable output.

### Config file

`~/.config/jora/config.toml` — multi-profile TOML. Profiles can store tokens in the config file, system keyring, or defer to `JORA_TOKEN`/`JIRA_API_TOKEN` env vars. The old `.env` vars (`JIRA_API_TOKEN`, `JIRA_SERVER`, etc.) still work without a config file.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Auth / general API error |
| 2 | Not found |
| 3 | Permission denied |
| 4 | Invalid input / not a TTY |

### Key invariants

- **`JoraClient` has no I/O.** All display logic lives in `utils/output.py` and command modules. The client only raises exceptions.
- **`--json` is always safe to pipe.** Even on error, JSON mode emits a `{"error": ..., "code": ...}` object to stdout (in addition to stderr text), so `jora ... --json | jq` never breaks.
- **`update_issue` avoids double-fetching.** It passes the already-fetched raw issue object to `_apply_estimate()` rather than re-fetching inside `set_original_estimate()`.
- **Time estimate editmeta fallback.** `_apply_estimate()` checks for `timetracking` field first, then `timeoriginalestimate` — this is required because availability depends on the Jira issue type and screen configuration on the target instance.

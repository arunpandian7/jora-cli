"""Configuration management for Jora.

Config file: ~/.config/jora/config.toml
Token resolution: JORA_TOKEN env var > keyring > config file
Profile resolution: --profile flag > JORA_PROFILE env var > defaults.profile > "default"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, field_validator

CONFIG_DIR = Path.home() / ".config" / "jora"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _load_toml(path: Path) -> dict:
    if sys.version_info >= (3, 11):
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    else:
        import tomli
        with open(path, "rb") as f:
            return tomli.load(f)


def _dump_toml(data: dict, path: Path) -> None:
    import tomli_w
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


class ConfigError(Exception):
    pass


class ProfileConfig(BaseModel):
    server: str
    username: Optional[str] = None
    token_source: str = "config"   # "config" | "keyring" | "env"
    token: Optional[str] = None
    verify_ssl: bool = True
    default_project: Optional[str] = None
    default_assignee: Optional[str] = None
    timezone: str = "UTC"

    @field_validator("token_source")
    @classmethod
    def validate_token_source(cls, v: str) -> str:
        if v not in ("config", "keyring", "env"):
            raise ValueError("token_source must be 'config', 'keyring', or 'env'")
        return v


class JoraConfig(BaseModel):
    defaults: dict = {}
    profiles: dict[str, ProfileConfig] = {}

    def get_profile(self, name: Optional[str] = None) -> ProfileConfig:
        profile_name = name or self.defaults.get("profile", "default")
        if profile_name not in self.profiles:
            raise ConfigError(
                f"Profile '{profile_name}' not found. Run 'jora config init' to set up."
            )
        return self.profiles[profile_name]

    def default_profile_name(self) -> str:
        return self.defaults.get("profile", "default")


def load_config() -> JoraConfig:
    """Load config from TOML file. Returns empty config if file doesn't exist."""
    try:
        data = _load_toml(CONFIG_FILE)
    except FileNotFoundError:
        return JoraConfig()
    profiles = {}
    for name, profile_data in data.get("profiles", {}).items():
        profiles[name] = ProfileConfig(**profile_data)
    return JoraConfig(defaults=data.get("defaults", {}), profiles=profiles)


def save_config(config: JoraConfig) -> None:
    """Persist config to TOML file."""
    data: dict = {"defaults": config.defaults, "profiles": {}}
    for name, profile in config.profiles.items():
        data["profiles"][name] = profile.model_dump(exclude_none=False)
    _dump_toml(data, CONFIG_FILE)


def resolve_token(profile: ProfileConfig, profile_name: str = "default") -> str:
    """Resolve the API token for the given profile.

    Order: JORA_TOKEN env var > keyring > config file token.
    Raises ConfigError if no token found.
    """
    # 1. Environment variable always wins
    env_token = os.getenv("JORA_TOKEN") or os.getenv("JIRA_API_TOKEN")  # backward compat
    if env_token:
        return env_token

    # 2. Keyring
    if profile.token_source == "keyring":
        try:
            import keyring
            stored = keyring.get_password("jora", profile_name)
            if stored:
                return stored
        except Exception:
            pass

    # 3. Config file token
    if profile.token:
        return profile.token

    raise ConfigError(
        "No API token found. Set JORA_TOKEN env var, or run 'jora config init'."
    )


def get_effective_profile(profile_name: Optional[str] = None) -> ProfileConfig:
    """Resolve the active profile, applying environment variable overrides.

    Profile resolution order:
    1. profile_name argument (from --profile flag)
    2. JORA_PROFILE env var
    3. defaults.profile in config.toml
    4. Auto-create from old env vars (backward compat)
    """
    name = profile_name or os.getenv("JORA_PROFILE")

    config = load_config()

    # Try to get from config
    if config.profiles:
        try:
            profile = config.get_profile(name)
        except ConfigError:
            if name:
                raise
            profile = list(config.profiles.values())[0]
    else:
        # No config file yet — try backward-compat env vars
        server = os.getenv("JIRA_SERVER", "https://your-jira-instance.example.com")
        username = os.getenv("JIRA_USERNAME")
        token = os.getenv("JIRA_API_TOKEN") or os.getenv("JORA_TOKEN")

        if not token:
            raise ConfigError(
                "No configuration found. Run 'jora config init' to set up, "
                "or set JORA_TOKEN and JIRA_SERVER environment variables."
            )

        profile = ProfileConfig(
            server=server,
            username=username,
            token_source="env",
            token=token,
            default_project=os.getenv("DEFAULT_PROJECT"),
            default_assignee=os.getenv("DEFAULT_ASSIGNEE"),
        )

    # Apply env var overrides to any profile
    server_override = os.getenv("JORA_SERVER")
    if server_override:
        profile = profile.model_copy(update={"server": server_override})

    return profile

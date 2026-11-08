"""Configuration loading and validation for the Discord bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

import dotenv


class ConfigError(ValueError):
    """Raised when required configuration is missing or malformed."""


@dataclass(frozen=True)
class BotConfig:
    token: str
    create_role_ids: tuple[int, ...]
    forum_channel_id: int
    projects_root: Path

    @property
    def role_id_set(self) -> set[int]:
        return set(self.create_role_ids)


def parse_role_ids(raw_roles: str) -> tuple[int, ...]:
    """Parse comma-separated Discord role IDs, validating integers and removing duplicates."""
    if not raw_roles or not raw_roles.strip():
        raise ConfigError("DISCORD_CREATE_ROLE_IDS must not be empty.")

    tokens = [token.strip() for token in raw_roles.split(",")]
    seen: set[int] = set()
    role_ids: list[int] = []

    for token in tokens:
        if not token:
            raise ConfigError("DISCORD_CREATE_ROLE_IDS contains an empty role entry.")
        if not token.isdigit():
            raise ConfigError(f"Invalid role ID '{token}': must be a positive integer.")
        role_id = int(token)
        if role_id <= 0:
            raise ConfigError(f"Invalid role ID '{token}': must be greater than zero.")
        if role_id not in seen:
            seen.add(role_id)
            role_ids.append(role_id)

    if not role_ids:
        raise ConfigError("DISCORD_CREATE_ROLE_IDS must contain at least one valid role ID.")

    return tuple(role_ids)


def load_bot_config(
    env: Optional[Mapping[str, str]] = None,
    dotenv_path: str | Path | None = None,
) -> BotConfig:
    """Load and validate bot configuration from environment variables."""
    if env is None:
        dotenv.load_dotenv(dotenv_path=dotenv_path, override=False)
        source = os.environ
    else:
        source = env

    token = source.get("DISCORD_TOKEN", "").strip()
    if not token:
        raise ConfigError("DISCORD_TOKEN environment variable is required.")

    raw_roles = source.get("DISCORD_CREATE_ROLE_IDS", "").strip()
    if not raw_roles:
        raise ConfigError("DISCORD_CREATE_ROLE_IDS environment variable is required.")

    create_role_ids = parse_role_ids(raw_roles)

    raw_forum_channel = source.get("DISCORD_LOCALIZE_NSW_CHANNEL_ID", "").strip()
    if not raw_forum_channel:
        raise ConfigError("DISCORD_LOCALIZE_NSW_CHANNEL_ID environment variable is required.")
    if not raw_forum_channel.isdigit():
        raise ConfigError(
            f"Invalid forum channel ID '{raw_forum_channel}': must be a positive integer."
        )
    forum_channel_id = int(raw_forum_channel)
    if forum_channel_id <= 0:
        raise ConfigError(
            f"Invalid forum channel ID '{raw_forum_channel}': must be greater than zero."
        )

    raw_projects_root = source.get("PROJECTS_ROOT", "projects").strip()
    projects_root = Path(raw_projects_root).resolve()

    return BotConfig(
        token=token,
        create_role_ids=create_role_ids,
        forum_channel_id=forum_channel_id,
        projects_root=projects_root,
    )

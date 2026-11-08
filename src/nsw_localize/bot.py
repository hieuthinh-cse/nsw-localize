"""Discord bot implementation for project workspace management."""

from __future__ import annotations

import contextlib
import inspect
import sys
from typing import Optional, Sequence

import discord
from discord import app_commands
from discord.ext import commands

from nsw_localize.auth import is_authorized_to_create_project
from nsw_localize.config import BotConfig, ConfigError, load_bot_config
from nsw_localize.project import (
    InvalidProjectNameError,
    ProjectError,
    ProjectExistsError,
    create_project_workspace,
    resolve_project_path,
)


async def handle_create_command(
    interaction: discord.Interaction,
    name: str,
    config: BotConfig,
) -> None:
    """Handle the /create application command."""
    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message(
            "This command can only be used within a server (guild).",
            ephemeral=True,
        )
        return

    is_admin = False
    permissions = getattr(interaction.user, "guild_permissions", None)
    if permissions is not None:
        is_admin = getattr(permissions, "administrator", False)

    role_ids = [role.id for role in getattr(interaction.user, "roles", [])]

    if not is_authorized_to_create_project(
        is_administrator=is_admin,
        member_role_ids=role_ids,
        allowed_role_ids=config.create_role_ids,
    ):
        await interaction.response.send_message(
            "You are not authorized to create project workspaces.",
            ephemeral=True,
        )
        return

    try:
        slug, project_dir = resolve_project_path(config.projects_root, name)
        if project_dir.exists():
            await interaction.response.send_message(
                f"Project already exists: Project '{slug}' already exists.",
                ephemeral=True,
            )
            return
    except InvalidProjectNameError as exc:
        await interaction.response.send_message(
            f"Invalid project name: {exc}",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)

    channel = interaction.guild.get_channel(config.forum_channel_id)
    if channel is None:
        try:
            channel = await interaction.guild.fetch_channel(config.forum_channel_id)
        except discord.DiscordException as exc:
            await interaction.followup.send(
                f"Configured forum channel {config.forum_channel_id} could not be accessed: {exc}",
                ephemeral=True,
            )
            return

    if not isinstance(channel, discord.ForumChannel):
        await interaction.followup.send(
            f"Configured channel {config.forum_channel_id} is not a Discord forum channel.",
            ephemeral=True,
        )
        return

    try:
        thread_result = await channel.create_thread(
            name=name,
            content=f"Discussion thread for project {name}.",
        )
    except discord.DiscordException as exc:
        await interaction.followup.send(
            f"Failed to create forum post: {exc}",
            ephemeral=True,
        )
        return

    thread = getattr(thread_result, "thread", thread_result)
    post_id = getattr(thread, "id", None)
    if post_id is None:
        post_id = getattr(thread_result, "id", None)

    try:
        created_dir = create_project_workspace(
            config.projects_root,
            name,
            forum_post_id=post_id,
        )
    except (ProjectError, discord.DiscordException) as exc:
        delete_coro = getattr(thread, "delete", None) or getattr(thread_result, "delete", None)
        if callable(delete_coro):
            with contextlib.suppress(discord.DiscordException):
                res = delete_coro()
                if inspect.isawaitable(res):
                    await res

        if isinstance(exc, ProjectExistsError):
            await interaction.followup.send(
                f"Project already exists: {exc}",
                ephemeral=True,
            )
        elif isinstance(exc, InvalidProjectNameError):
            await interaction.followup.send(
                f"Invalid project name: {exc}",
                ephemeral=True,
            )
        elif isinstance(exc, ProjectError):
            await interaction.followup.send(
                f"Failed to create workspace: {exc}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"An unexpected error occurred while creating project: {exc}",
                ephemeral=True,
            )
        return

    await interaction.followup.send(
        f"Successfully created project workspace '{created_dir.name}' and forum post (ID: {post_id}).",
        ephemeral=True,
    )


async def handle_forum_mention(
    message: discord.Message,
    config: BotConfig,
    bot_user: discord.User | discord.ClientUser | None,
) -> bool:
    """Handle message mentions in forum post threads. Returns True if a reply was sent."""
    if bot_user is None:
        return False

    if getattr(message.author, "bot", False) or message.author == bot_user:
        return False

    if bot_user not in getattr(message, "mentions", []):
        return False

    channel = getattr(message, "channel", None)
    if not isinstance(channel, discord.Thread):
        return False

    if getattr(channel, "parent_id", None) != config.forum_channel_id:
        return False

    author = getattr(message, "author", None)
    if not isinstance(author, discord.Member):
        return False

    is_admin = False
    permissions = getattr(author, "guild_permissions", None)
    if permissions is not None:
        is_admin = getattr(permissions, "administrator", False)

    role_ids = [role.id for role in getattr(author, "roles", [])]

    if not is_authorized_to_create_project(
        is_administrator=is_admin,
        member_role_ids=role_ids,
        allowed_role_ids=config.create_role_ids,
    ):
        return False

    await message.reply("hi", mention_author=True)
    return True


class LocalizationBot(commands.Bot):
    """Discord bot that provides localization project commands."""

    def __init__(self, config: BotConfig, **kwargs) -> None:
        intents = kwargs.pop("intents", None)
        if intents is None:
            intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents, **kwargs)
        self.config = config
        self._register_commands()

    def _register_commands(self) -> None:
        @self.tree.command(
            name="create",
            description="Initialize a new localization project workspace",
        )
        @app_commands.describe(name="The name of the localization project to create")
        async def create(interaction: discord.Interaction, name: str) -> None:
            await handle_create_command(interaction, name, self.config)

    async def on_message(self, message: discord.Message) -> None:
        await self.process_commands(message)
        await handle_forum_mention(message, self.config, self.user)

    async def setup_hook(self) -> None:
        """Synchronize slash commands with Discord upon startup."""
        await self.tree.sync()


def create_bot(config: BotConfig) -> LocalizationBot:
    """Construct and configure the localization Discord bot without connecting."""
    return LocalizationBot(config=config)


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        config = load_bot_config()
    except ConfigError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return 1

    bot = create_bot(config)
    bot.run(config.token)
    return 0


if __name__ == "__main__":
    sys.exit(main())

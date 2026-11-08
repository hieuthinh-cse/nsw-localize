"""Unit and integration tests for Discord bot interaction handlers and registration."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import yaml

from nsw_localize.bot import (
    LocalizationBot,
    create_bot,
    handle_create_command,
    handle_forum_mention,
)
from nsw_localize.config import BotConfig
from nsw_localize.project import ProjectError


class TestBotCommandHandlers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name).resolve()
        self.config = BotConfig(
            token="test-token",
            create_role_ids=(111, 222),
            forum_channel_id=123456789,
            projects_root=self.projects_root,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _make_interaction(
        self,
        *,
        is_guild: bool = True,
        is_admin: bool = False,
        role_ids: list[int] | None = None,
        forum_channel: discord.ForumChannel | None = None,
    ) -> AsyncMock:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()

        if not is_guild:
            interaction.guild = None
            interaction.user = MagicMock(spec=discord.User)
            return interaction

        interaction.guild = MagicMock(spec=discord.Guild)
        member = MagicMock(spec=discord.Member)
        member.guild_permissions.administrator = is_admin

        roles = []
        for r_id in role_ids or []:
            role = MagicMock(spec=discord.Role)
            role.id = r_id
            roles.append(role)
        member.roles = roles

        interaction.user = member

        if forum_channel is None:
            default_forum = MagicMock(spec=discord.ForumChannel)
            default_forum.id = self.config.forum_channel_id
            mock_thread = MagicMock(spec=discord.Thread)
            mock_thread.id = 555666777
            mock_thread.delete = AsyncMock()
            default_forum.create_thread = AsyncMock(return_value=mock_thread)
            forum_channel = default_forum

        interaction.guild.get_channel = MagicMock(return_value=forum_channel)
        interaction.guild.fetch_channel = AsyncMock(return_value=forum_channel)

        return interaction

    async def test_allowed_role_creates_workspace(self) -> None:
        interaction = self._make_interaction(is_admin=False, role_ids=[111])

        await handle_create_command(interaction, "Zelda Echoes", self.config)

        expected_dir = self.projects_root / "zelda-echoes"
        self.assertTrue(expected_dir.is_dir())
        manifest_path = expected_dir / "workflow.yaml"
        self.assertTrue(manifest_path.is_file())

        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["forum_post_id"], 555666777)

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("zelda-echoes", args[0])
        self.assertIn("created", args[0].lower())

    async def test_administrator_creates_workspace(self) -> None:
        interaction = self._make_interaction(is_admin=True, role_ids=[])

        await handle_create_command(interaction, "Metroid Prime", self.config)

        expected_dir = self.projects_root / "metroid-prime"
        self.assertTrue(expected_dir.is_dir())

        interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("metroid-prime", args[0])

    async def test_unauthorized_member_denied(self) -> None:
        interaction = self._make_interaction(is_admin=False, role_ids=[999])

        await handle_create_command(interaction, "Unauthorized Game", self.config)

        self.assertFalse((self.projects_root / "unauthorized-game").exists())
        interaction.response.send_message.assert_awaited_once()
        args, kwargs = interaction.response.send_message.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("not authorized", args[0].lower())

    async def test_direct_message_rejected(self) -> None:
        interaction = self._make_interaction(is_guild=False)

        await handle_create_command(interaction, "DM Game", self.config)

        self.assertFalse((self.projects_root / "dm-game").exists())
        interaction.response.send_message.assert_awaited_once()
        args, kwargs = interaction.response.send_message.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("server", args[0].lower())

    async def test_invalid_name_rejected(self) -> None:
        interaction = self._make_interaction(is_admin=True)

        await handle_create_command(interaction, "../traversal", self.config)

        interaction.response.send_message.assert_awaited_once()
        args, kwargs = interaction.response.send_message.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("invalid project name", args[0].lower())

    async def test_duplicate_project_rejected(self) -> None:
        interaction1 = self._make_interaction(is_admin=True)
        await handle_create_command(interaction1, "Dup Game", self.config)

        interaction2 = self._make_interaction(is_admin=True)
        await handle_create_command(interaction2, "Dup Game", self.config)

        interaction2.response.send_message.assert_awaited_once()
        args, kwargs = interaction2.response.send_message.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("already exists", args[0].lower())

    async def test_channel_not_found_returns_error(self) -> None:
        interaction = self._make_interaction(is_admin=True)
        interaction.guild.get_channel.return_value = None
        interaction.guild.fetch_channel.side_effect = discord.NotFound(
            MagicMock(), "Channel not found"
        )

        await handle_create_command(interaction, "Lost Channel Game", self.config)

        self.assertFalse((self.projects_root / "lost-channel-game").exists())
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("could not be accessed", args[0].lower())

    async def test_channel_inaccessible_returns_error(self) -> None:
        interaction = self._make_interaction(is_admin=True)
        interaction.guild.get_channel.return_value = None
        interaction.guild.fetch_channel.side_effect = discord.Forbidden(
            MagicMock(), "Missing access"
        )

        await handle_create_command(interaction, "Forbidden Channel Game", self.config)

        self.assertFalse((self.projects_root / "forbidden-channel-game").exists())
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("could not be accessed", args[0].lower())

    async def test_wrong_channel_type_returns_error(self) -> None:
        text_channel = MagicMock(spec=discord.TextChannel)
        text_channel.id = self.config.forum_channel_id
        interaction = self._make_interaction(is_admin=True, forum_channel=text_channel)

        await handle_create_command(interaction, "Wrong Channel Game", self.config)

        self.assertFalse((self.projects_root / "wrong-channel-game").exists())
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("not a discord forum channel", args[0].lower())

    async def test_forum_post_creation_failure_stops_workspace_creation(self) -> None:
        interaction = self._make_interaction(is_admin=True)
        forum = interaction.guild.get_channel.return_value
        forum.create_thread.side_effect = discord.HTTPException(
            MagicMock(), "Forum API rate limit"
        )

        with patch("nsw_localize.bot.create_project_workspace") as mock_create_ws:
            await handle_create_command(interaction, "Api Fail Game", self.config)
            mock_create_ws.assert_not_called()

        self.assertFalse((self.projects_root / "api-fail-game").exists())
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("failed to create forum post", args[0].lower())

    async def test_workspace_failure_after_forum_post_compensates_deletion(self) -> None:
        interaction = self._make_interaction(is_admin=True)
        forum = interaction.guild.get_channel.return_value
        mock_thread = forum.create_thread.return_value

        with patch(
            "nsw_localize.bot.create_project_workspace",
            side_effect=ProjectError("Filesystem permission denied"),
        ):
            await handle_create_command(interaction, "Failing Project", self.config)

        mock_thread.delete.assert_awaited_once()
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("failed to create workspace", args[0].lower())

    async def test_workspace_failure_compensates_even_if_post_deletion_fails(self) -> None:
        interaction = self._make_interaction(is_admin=True)
        forum = interaction.guild.get_channel.return_value
        mock_thread = forum.create_thread.return_value
        mock_thread.delete.side_effect = discord.HTTPException(
            MagicMock(), "Thread delete failed"
        )

        with patch(
            "nsw_localize.bot.create_project_workspace",
            side_effect=ProjectError("Filesystem permission denied"),
        ):
            await handle_create_command(interaction, "Failing Project", self.config)

        mock_thread.delete.assert_awaited_once()
        interaction.followup.send.assert_awaited_once()
        args, kwargs = interaction.followup.send.call_args
        self.assertTrue(kwargs.get("ephemeral"))
        self.assertIn("failed to create workspace", args[0].lower())


class TestForumMentionHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.config = BotConfig(
            token="test-token",
            create_role_ids=(111, 222),
            forum_channel_id=123456789,
            projects_root=Path("/tmp/projects"),
        )
        self.bot_user = MagicMock(spec=discord.ClientUser)
        self.bot_user.id = 999000

    def _make_mention_message(
        self,
        *,
        is_bot: bool = False,
        is_self: bool = False,
        is_thread: bool = True,
        parent_id: int | None = 123456789,
        is_admin: bool = False,
        role_ids: list[int] | None = None,
        is_mentioned: bool = True,
        is_member: bool = True,
    ) -> MagicMock:
        message = MagicMock(spec=discord.Message)
        message.reply = AsyncMock()

        if is_self:
            message.author = self.bot_user
        elif is_member:
            author = MagicMock(spec=discord.Member)
            author.bot = is_bot
            author.guild_permissions.administrator = is_admin
            roles = []
            for r_id in role_ids or []:
                role = MagicMock(spec=discord.Role)
                role.id = r_id
                roles.append(role)
            author.roles = roles
            message.author = author
        else:
            author = MagicMock(spec=discord.User)
            author.bot = is_bot
            message.author = author

        if is_thread:
            channel = MagicMock(spec=discord.Thread)
            channel.parent_id = parent_id
            message.channel = channel
        else:
            channel = MagicMock(spec=discord.TextChannel)
            message.channel = channel

        if is_mentioned:
            message.mentions = [self.bot_user]
        else:
            message.mentions = []

        return message

    async def test_authorized_role_mention_replies(self) -> None:
        message = self._make_mention_message(role_ids=[111])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertTrue(replied)
        message.reply.assert_awaited_once_with("hi", mention_author=True)

    async def test_admin_mention_replies(self) -> None:
        message = self._make_mention_message(is_admin=True, role_ids=[])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertTrue(replied)
        message.reply.assert_awaited_once_with("hi", mention_author=True)

    async def test_unauthorized_member_silence(self) -> None:
        message = self._make_mention_message(is_admin=False, role_ids=[999])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_bot_author_silence(self) -> None:
        message = self._make_mention_message(is_bot=True, role_ids=[111])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_author_is_bot_user_silence(self) -> None:
        message = self._make_mention_message(is_self=True)
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_non_forum_thread_silence(self) -> None:
        message = self._make_mention_message(parent_id=987654321, role_ids=[111])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_plain_text_channel_silence(self) -> None:
        message = self._make_mention_message(is_thread=False, role_ids=[111])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_bot_not_mentioned_silence(self) -> None:
        message = self._make_mention_message(is_mentioned=False, role_ids=[111])
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_non_member_author_silence(self) -> None:
        message = self._make_mention_message(is_member=False)
        replied = await handle_forum_mention(message, self.config, self.bot_user)
        self.assertFalse(replied)
        message.reply.assert_not_called()

    async def test_bot_on_message_handles_mention(self) -> None:
        bot = create_bot(self.config)
        bot._connection.user = self.bot_user
        message = self._make_mention_message(role_ids=[111])

        with patch.object(bot, "process_commands", new_callable=AsyncMock) as mock_process:
            await bot.on_message(message)
            mock_process.assert_awaited_once_with(message)
            message.reply.assert_awaited_once_with("hi", mention_author=True)


class TestBotConstructionAndSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BotConfig(
            token="dummy-token",
            create_role_ids=(123, 456),
            forum_channel_id=123456789,
            projects_root=Path("/tmp/projects"),
        )

    def test_create_bot_registers_slash_command(self) -> None:
        bot = create_bot(self.config)
        self.assertIsInstance(bot, LocalizationBot)
        self.assertTrue(bot.intents.message_content)

        create_cmd = bot.tree.get_command("create")
        self.assertIsNotNone(create_cmd)
        self.assertEqual(create_cmd.name, "create")
        self.assertIn("project", create_cmd.description.lower())

    def test_setup_hook_synchronizes_commands(self) -> None:
        bot = create_bot(self.config)

        with patch.object(bot.tree, "sync", new_callable=AsyncMock) as mock_sync:
            asyncio.run(bot.setup_hook())
            mock_sync.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()

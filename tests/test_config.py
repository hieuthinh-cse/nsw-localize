"""Unit tests for bot configuration parsing."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nsw_localize.config import ConfigError, load_bot_config, parse_role_ids


class TestConfig(unittest.TestCase):
    def test_valid_config(self) -> None:
        env = {
            "DISCORD_TOKEN": "secret-token-123",
            "DISCORD_CREATE_ROLE_IDS": "1001, 1002, 1003",
            "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "1568872535125393458",
            "PROJECTS_ROOT": "/tmp/custom_projects",
        }
        cfg = load_bot_config(env)
        self.assertEqual(cfg.token, "secret-token-123")
        self.assertEqual(cfg.create_role_ids, (1001, 1002, 1003))
        self.assertEqual(cfg.role_id_set, {1001, 1002, 1003})
        self.assertEqual(cfg.forum_channel_id, 1568872535125393458)
        self.assertEqual(cfg.projects_root, Path("/tmp/custom_projects").resolve())

    def test_default_projects_root(self) -> None:
        env = {
            "DISCORD_TOKEN": "token",
            "DISCORD_CREATE_ROLE_IDS": "123",
            "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "987654",
        }
        cfg = load_bot_config(env)
        self.assertEqual(cfg.forum_channel_id, 987654)
        self.assertEqual(cfg.projects_root, Path("projects").resolve())

    def test_missing_token(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_bot_config({
                "DISCORD_CREATE_ROLE_IDS": "123",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "987654",
            })
        self.assertIn("DISCORD_TOKEN", str(ctx.exception))

        with self.assertRaises(ConfigError):
            load_bot_config({
                "DISCORD_TOKEN": "   ",
                "DISCORD_CREATE_ROLE_IDS": "123",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "987654",
            })

    def test_missing_role_ids(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_bot_config({
                "DISCORD_TOKEN": "valid-token",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "987654",
            })
        self.assertIn("DISCORD_CREATE_ROLE_IDS", str(ctx.exception))

        with self.assertRaises(ConfigError):
            load_bot_config({
                "DISCORD_TOKEN": "valid-token",
                "DISCORD_CREATE_ROLE_IDS": "   ",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "987654",
            })

    def test_missing_forum_channel_id(self) -> None:
        with self.assertRaises(ConfigError) as ctx:
            load_bot_config({
                "DISCORD_TOKEN": "valid-token",
                "DISCORD_CREATE_ROLE_IDS": "123",
            })
        self.assertIn("DISCORD_LOCALIZE_NSW_CHANNEL_ID", str(ctx.exception))

        with self.assertRaises(ConfigError):
            load_bot_config({
                "DISCORD_TOKEN": "valid-token",
                "DISCORD_CREATE_ROLE_IDS": "123",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "   ",
            })

    def test_malformed_forum_channel_id(self) -> None:
        malformed_cases = ["abc", "123a", "12.34", "123,456", "   xyz   "]
        for case in malformed_cases:
            with self.subTest(case=case), self.assertRaises(ConfigError):
                load_bot_config({
                    "DISCORD_TOKEN": "valid-token",
                    "DISCORD_CREATE_ROLE_IDS": "123",
                    "DISCORD_LOCALIZE_NSW_CHANNEL_ID": case,
                })

    def test_non_positive_forum_channel_id(self) -> None:
        non_positive_cases = ["0", "-1", "-123"]
        for case in non_positive_cases:
            with self.subTest(case=case), self.assertRaises(ConfigError):
                load_bot_config({
                    "DISCORD_TOKEN": "valid-token",
                    "DISCORD_CREATE_ROLE_IDS": "123",
                    "DISCORD_LOCALIZE_NSW_CHANNEL_ID": case,
                })

    def test_malformed_role_ids(self) -> None:
        invalid_cases = [
            "abc",
            "123, abc",
            "-5",
            "0",
            "123,,456",
            ",123",
            "123,",
            "12.34",
        ]
        for case in invalid_cases:
            with self.subTest(case=case), self.assertRaises(ConfigError):
                parse_role_ids(case)

    def test_duplicate_role_ids(self) -> None:
        ids = parse_role_ids("101, 202, 101, 303, 202")
        self.assertEqual(ids, (101, 202, 303))
        self.assertEqual(set(ids), {101, 202, 303})

    def test_dotenv_loading_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(
                "DISCORD_TOKEN=token-from-dotenv\n"
                "DISCORD_CREATE_ROLE_IDS=901, 902\n"
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID=888888\n"
            )
            with patch.dict(os.environ, {}, clear=True):
                cfg = load_bot_config(dotenv_path=env_file)
                self.assertEqual(cfg.token, "token-from-dotenv")
                self.assertEqual(cfg.create_role_ids, (901, 902))
                self.assertEqual(cfg.forum_channel_id, 888888)

    def test_os_environ_precedence_over_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(
                "DISCORD_TOKEN=token-from-dotenv\n"
                "DISCORD_CREATE_ROLE_IDS=901, 902\n"
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID=888888\n"
            )
            env_override = {
                "DISCORD_TOKEN": "token-from-os-environ",
                "DISCORD_CREATE_ROLE_IDS": "777",
                "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "111111",
            }
            with patch.dict(os.environ, env_override, clear=True):
                cfg = load_bot_config(dotenv_path=env_file)
                self.assertEqual(cfg.token, "token-from-os-environ")
                self.assertEqual(cfg.create_role_ids, (777,))
                self.assertEqual(cfg.forum_channel_id, 111111)

    def test_missing_dotenv_file_graceful(self) -> None:
        env_vars = {
            "DISCORD_TOKEN": "valid-token",
            "DISCORD_CREATE_ROLE_IDS": "123",
            "DISCORD_LOCALIZE_NSW_CHANNEL_ID": "456",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            non_existent = Path("/nonexistent/path/.env")
            cfg = load_bot_config(dotenv_path=non_existent)
            self.assertEqual(cfg.token, "valid-token")
            self.assertEqual(cfg.create_role_ids, (123,))
            self.assertEqual(cfg.forum_channel_id, 456)


if __name__ == "__main__":
    unittest.main()

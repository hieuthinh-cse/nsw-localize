"""Unit tests for project slug normalization and path resolution."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from nsw_localize.project import (
    InvalidProjectNameError,
    ProjectError,
    ProjectExistsError,
    create_project_workspace,
    normalize_project_slug,
    resolve_project_path,
)


class TestProjectNameResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("/dummy/projects_root")

    def test_normalization(self) -> None:
        cases = [
            ("My Game", "my-game"),
            ("Pokemon Scarlet (NSW)", "pokemon-scarlet-nsw"),
            ("TEST__game   123", "test-game-123"),
            ("already-slug", "already-slug"),
            ("  leading and trailing  ", "leading-and-trailing"),
            ("Super_Mario_Odyssey", "super-mario-odyssey"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                slug = normalize_project_slug(raw)
                self.assertEqual(slug, expected)

    def test_reject_empty(self) -> None:
        empty_cases = ["", "   ", "\t\n", "---", "!@#$%", "   ...   "]
        for case in empty_cases:
            with self.subTest(case=case), self.assertRaises(InvalidProjectNameError):
                normalize_project_slug(case)

    def test_reject_separators(self) -> None:
        sep_cases = [
            "foo/bar",
            "/foo",
            "foo/",
            "foo\\bar",
            "\\foo",
            "nested/dir/game",
        ]
        for case in sep_cases:
            with self.subTest(case=case), self.assertRaises(InvalidProjectNameError):
                normalize_project_slug(case)

    def test_reject_traversal_and_dots(self) -> None:
        dot_cases = [
            ".",
            "..",
            "../escape",
            "..\\escape",
        ]
        for case in dot_cases:
            with self.subTest(case=case), self.assertRaises(InvalidProjectNameError):
                normalize_project_slug(case)

    def test_resolve_project_path_valid(self) -> None:
        slug, path = resolve_project_path(self.root, "My Game")
        self.assertEqual(slug, "my-game")
        self.assertEqual(path, self.root.resolve() / "my-game")

    def test_resolve_project_path_rejects_escape(self) -> None:
        escape_cases = [
            "../outside",
            "/etc/passwd",
            "..",
            "sub/dir",
        ]
        for case in escape_cases:
            with self.subTest(case=case), self.assertRaises(InvalidProjectNameError):
                resolve_project_path(self.root, case)


class TestWorkspaceCreation(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name).resolve()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_workspace_layout_and_manifest(self) -> None:
        project_dir = create_project_workspace(
            self.projects_root,
            "  My Awesome Game (NSW)  ",
            forum_post_id=987654321,
        )
        expected_slug = "my-awesome-game-nsw"
        expected_dir = self.projects_root / expected_slug

        self.assertEqual(project_dir, expected_dir)
        self.assertTrue(project_dir.is_dir())
        self.assertTrue((project_dir / "rom" / "base").is_dir())
        self.assertTrue((project_dir / "rom" / "update").is_dir())
        self.assertTrue((project_dir / "output").is_dir())

        manifest_file = project_dir / "workflow.yaml"
        self.assertTrue(manifest_file.is_file())

        with open(manifest_file, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        expected_manifest = {
            "name": "My Awesome Game (NSW)",
            "version": 1,
            "forum_post_id": 987654321,
            "game": {
                "input": [
                    {"base": "./rom/base/"},
                    {"update": "./rom/update/"},
                ],
                "output": "./output/",
            },
        }
        self.assertEqual(manifest, expected_manifest)
        self.assertIsInstance(manifest["version"], int)
        self.assertIsInstance(manifest["forum_post_id"], int)
        self.assertEqual(manifest["forum_post_id"], 987654321)

    def test_existing_directory_preserved_and_raises(self) -> None:
        existing_dir = self.projects_root / "existing-game"
        existing_dir.mkdir(parents=True)
        canary_file = existing_dir / "custom_data.txt"
        canary_file.write_text("critical user content", encoding="utf-8")

        with self.assertRaises(ProjectExistsError):
            create_project_workspace(self.projects_root, "Existing Game", forum_post_id=123)

        # Ensure existing directory and its contents are completely unchanged
        self.assertTrue(canary_file.is_file())
        self.assertEqual(canary_file.read_text(encoding="utf-8"), "critical user content")
        self.assertFalse((existing_dir / "workflow.yaml").exists())

    def test_failure_cleanup_limited_to_request_created_paths(self) -> None:
        pre_existing = self.projects_root / "other-game"
        pre_existing.mkdir(parents=True)
        other_canary = pre_existing / "keep_me.txt"
        other_canary.write_text("keep this safe", encoding="utf-8")

        # Simulate failure during manifest write for new project
        with patch.object(
            Path, "write_text", side_effect=OSError("Disk full simulation")
        ), self.assertRaises(ProjectError):
            create_project_workspace(
                self.projects_root,
                "New Failing Project",
                forum_post_id=12345,
            )

        failed_dir = self.projects_root / "new-failing-project"
        self.assertFalse(failed_dir.exists())

        # Ensure pre-existing directory was not affected
        self.assertTrue(pre_existing.is_dir())
        self.assertTrue(other_canary.is_file())
        self.assertEqual(other_canary.read_text(encoding="utf-8"), "keep this safe")

    def test_invalid_forum_post_id_raises_and_cleans_up(self) -> None:
        invalid_ids = [0, -1, -999, "not-an-int", None, True, False]
        for invalid_id in invalid_ids:
            with self.subTest(forum_post_id=invalid_id):
                with self.assertRaises(ProjectError):
                    create_project_workspace(
                        self.projects_root,
                        "Rollback Game",
                        forum_post_id=invalid_id,  # type: ignore
                    )
                self.assertFalse((self.projects_root / "rollback-game").exists())


if __name__ == "__main__":
    unittest.main()

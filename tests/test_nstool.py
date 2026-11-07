"""Tests for NSTool executable discovery."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nsw_localize.nstool import (
    NstoolError,
    NstoolProcessError,
    ValidationError,
    build_nca_extract_args,
    build_nca_merge_args,
    build_nsp_extract_args,
    prepare_output_directory,
    resolve_keyset,
    resolve_nstool,
    run_nstool,
    validate_input_file,
)


class ResolveNstoolTests(unittest.TestCase):
    def test_uses_runnable_bundled_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = root / "nstool"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(executable.stat().st_mode | os.X_OK)

            with (
                patch("sys.platform", "darwin"),
                patch("nsw_localize.nstool.os.access", return_value=True),
            ):
                self.assertEqual(resolve_nstool(repository_root=root), executable.resolve())

    def test_resolves_nstool_exe_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            exe = root / "nstool.exe"
            exe.write_bytes(b"MZ\x00\x00")
            nix = root / "nstool"
            nix.write_text("#!/bin/sh\n", encoding="utf-8")

            with patch("sys.platform", "win32"):
                self.assertEqual(resolve_nstool(repository_root=root), exe.resolve())

    def test_resolves_nstool_on_posix_when_both_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            exe = root / "nstool.exe"
            exe.write_bytes(b"MZ\x00\x00")
            nix = root / "nstool"
            nix.write_text("#!/bin/sh\n", encoding="utf-8")
            nix.chmod(nix.stat().st_mode | os.X_OK)

            with (
                patch("sys.platform", "darwin"),
                patch("nsw_localize.nstool.os.access", return_value=True),
            ):
                self.assertEqual(resolve_nstool(repository_root=root), nix.resolve())

    def test_fallback_to_nstool_on_windows_if_exe_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nix = root / "nstool"
            nix.write_text("#!/bin/sh\n", encoding="utf-8")

            with (
                patch("sys.platform", "win32"),
                patch("nsw_localize.nstool.os.access", return_value=True),
            ):
                self.assertEqual(resolve_nstool(repository_root=root), nix.resolve())

    def test_fallback_to_exe_on_posix_if_nix_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            exe = root / "nstool.exe"
            exe.write_bytes(b"MZ\x00\x00")
            exe.chmod(exe.stat().st_mode | os.X_OK)

            with (
                patch("sys.platform", "linux"),
                patch("nsw_localize.nstool.os.access", return_value=True),
            ):
                self.assertEqual(resolve_nstool(repository_root=root), exe.resolve())

    def test_uses_explicit_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = Path(temporary_directory) / "custom-nstool"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(executable.stat().st_mode | os.X_OK)

            with patch("nsw_localize.nstool.os.access", return_value=True):
                self.assertEqual(resolve_nstool(executable), executable.resolve())

    def test_explicit_override_not_swapped_with_exe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "nstool.exe").write_bytes(b"MZ\x00\x00")
            # User specifically passed path ending with "nstool" which does not exist
            missing_override = root / "nstool"

            with (
                patch("sys.platform", "win32"),
                self.assertRaisesRegex(NstoolError, "--nstool"),
            ):
                resolve_nstool(missing_override)

    def test_rejects_missing_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing-nstool"

            with self.assertRaisesRegex(NstoolError, "--nstool"):
                resolve_nstool(missing)

    def test_rejects_non_executable_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = Path(temporary_directory) / "nstool"
            executable.write_text("not executable", encoding="utf-8")
            executable.chmod(0o600)

            with (
                patch("sys.platform", "darwin"),
                patch("nsw_localize.nstool.os.access", return_value=False),
                self.assertRaisesRegex(NstoolError, "not runnable"),
            ):
                resolve_nstool(executable)


class ResolveKeysetTests(unittest.TestCase):
    def test_uses_explicit_keyset_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            keyset = Path(temporary_directory) / "custom.keys"
            keyset.write_text("keys", encoding="utf-8")
            self.assertEqual(resolve_keyset(keyset), keyset.resolve())

    def test_uses_default_keyset_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            default_keyset = Path(temporary_directory) / "prod.keys"
            default_keyset.write_text("keys", encoding="utf-8")

            with patch("nsw_localize.nstool.Path.expanduser", return_value=default_keyset):
                self.assertEqual(resolve_keyset(None), default_keyset.resolve())

    def test_rejects_missing_default_keyset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_keyset = Path(temporary_directory) / "nonexistent.keys"

            with (
                patch("nsw_localize.nstool.Path.expanduser", return_value=missing_keyset),
                self.assertRaisesRegex(ValidationError, "Keyset not found"),
            ):
                resolve_keyset(None)


class PathValidationTests(unittest.TestCase):
    def test_accepts_readable_nsp_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            nsp = Path(temporary_directory) / "game.nsp"
            nsp.write_bytes(b"package")

            self.assertEqual(validate_input_file(nsp, "NSP input", ".nsp"), nsp.resolve())

    def test_rejects_missing_or_wrong_extension_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            wrong_extension = root / "game.txt"
            wrong_extension.write_text("not an NSP", encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "existing regular file"):
                validate_input_file(root / "missing.nsp", "NSP input", ".nsp")
            with self.assertRaisesRegex(ValidationError, "extension"):
                validate_input_file(wrong_extension, "NSP input", ".nsp")

    def test_creates_missing_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "new-output"

            self.assertEqual(
                prepare_output_directory(destination, overwrite=False), destination.resolve()
            )
            self.assertTrue(destination.is_dir())

    def test_rejects_non_empty_output_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "output"
            destination.mkdir()
            (destination / "existing.txt").write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(ValidationError, "not empty"):
                prepare_output_directory(destination, overwrite=False)
            self.assertEqual((destination / "existing.txt").read_text(encoding="utf-8"), "keep")

    def test_accepts_non_empty_output_with_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "output"
            destination.mkdir()
            (destination / "existing.txt").write_text("keep", encoding="utf-8")

            self.assertEqual(
                prepare_output_directory(destination, overwrite=True), destination.resolve()
            )


class NstoolProcessTests(unittest.TestCase):
    def test_builds_expected_nsp_and_nca_arguments(self) -> None:
        self.assertEqual(
            build_nsp_extract_args(Path("game.nsp"), Path("output")),
            ["-x", "/", "output", "game.nsp"],
        )
        self.assertEqual(
            build_nca_extract_args(Path("game.nca"), Path("prod.keys"), Path("romfs"), "/0"),
            ["-k", "prod.keys", "-x", "/0", "romfs", "game.nca"],
        )
        self.assertEqual(
            build_nca_merge_args(
                Path("base.nca"),
                Path("patch.nca"),
                Path("prod.keys"),
                Path("romfs"),
                tik_path=Path("patch.tik"),
            ),
            [
                "-k",
                "prod.keys",
                "--tik",
                "patch.tik",
                "--basenca",
                "base.nca",
                "-x",
                "/1",
                "romfs",
                "patch.nca",
            ],
        )

    @patch("nsw_localize.nstool.subprocess.run")
    def test_runs_argument_list_without_a_shell(self, mocked_run) -> None:  # type: ignore[no-untyped-def]
        mocked_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="done", stderr=""
        )

        result = run_nstool(
            Path("/tools/nstool"), ["-x", "/", "out", "game.nsp"], operation="NSP extraction"
        )

        self.assertEqual(result.stdout, "done")
        mocked_run.assert_called_once_with(
            ["/tools/nstool", "-x", "/", "out", "game.nsp"],
            check=False,
            capture_output=True,
            text=True,
        )

    @patch("nsw_localize.nstool.subprocess.run")
    def test_preserves_tool_diagnostic_without_exposing_keyset(self, mocked_run) -> None:  # type: ignore[no-untyped-def]
        mocked_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=4, stdout="", stderr="bad title key"
        )

        with self.assertRaisesRegex(NstoolProcessError, "bad title key") as caught:
            run_nstool(
                Path("/tools/nstool"),
                ["-k", "/secret/prod.keys", "-x", "/", "out", "game.nca"],
                operation="NCA extraction",
            )

        self.assertNotIn("/secret/prod.keys", str(caught.exception))

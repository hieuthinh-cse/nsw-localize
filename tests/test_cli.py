"""Command-level tests for the unpacking CLI."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from nsw_localize.cli import build_parser, main
from nsw_localize.nstool import NstoolProcessError


class CliTests(unittest.TestCase):
    def test_parser_structure(self) -> None:
        parser = build_parser()
        self.assertEqual(parser.prog, "nsl")

        # Test root help
        stdout = io.StringIO()
        with self.assertRaises(SystemExit) as exit_check, redirect_stdout(stdout):
            parser.parse_args(["--help"])
        self.assertEqual(exit_check.exception.code, 0)
        self.assertIn("unpack", stdout.getvalue())
        self.assertIn("merge-nca", stdout.getvalue())

        # Test unpack help
        stdout = io.StringIO()
        with self.assertRaises(SystemExit) as exit_check, redirect_stdout(stdout):
            parser.parse_args(["unpack", "--help"])
        self.assertEqual(exit_check.exception.code, 0)
        self.assertIn("nsp", stdout.getvalue())
        self.assertIn("nca", stdout.getvalue())

    def test_direct_nsp_without_unpack_fails(self) -> None:
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as exit_check, redirect_stderr(stderr):
            main(["nsp", "game.nsp", "--output", "out"])
        self.assertEqual(exit_check.exception.code, 2)
        self.assertIn("invalid choice", stderr.getvalue())

    def test_direct_nca_without_unpack_fails(self) -> None:
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as exit_check, redirect_stderr(stderr):
            main(["nca", "game.nca", "--keyset", "prod.keys", "--output", "out"])
        self.assertEqual(exit_check.exception.code, 2)
        self.assertIn("invalid choice", stderr.getvalue())

    def test_nsp_extracts_and_reports_nca_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "game.nsp"
            package.write_bytes(b"package")
            output = root / "out"

            def extract_nsp(*_args, **_kwargs):  # type: ignore[no-untyped-def]
                (output / "program.nca").write_bytes(b"nca")

            stdout = io.StringIO()
            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch("nsw_localize.cli.run_nstool", side_effect=extract_nsp) as mocked_run,
                redirect_stdout(stdout),
            ):
                exit_code = main(["unpack", "nsp", str(package), "--output", str(output)])

            self.assertEqual(exit_code, 0)
            mocked_run.assert_called_once()
            self.assertIn("program.nca", stdout.getvalue())

    def test_invalid_nsp_does_not_invoke_runner(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("nsw_localize.cli.run_nstool") as mocked_run,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            exit_code = main(["unpack", "nsp", "missing.nsp", "--output", "out"])

        self.assertEqual(exit_code, 2)
        mocked_run.assert_not_called()
        self.assertIn("existing regular file", stderr.getvalue())

    def test_non_empty_destination_does_not_invoke_runner_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "game.nsp"
            package.write_bytes(b"package")
            output = root / "out"
            output.mkdir()
            (output / "existing.txt").write_text("keep", encoding="utf-8")

            stderr = io.StringIO()
            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch("nsw_localize.cli.run_nstool") as mocked_run,
                redirect_stderr(stderr),
            ):
                exit_code = main(["unpack", "nsp", str(package), "--output", str(output)])

            self.assertEqual(exit_code, 2)
            mocked_run.assert_not_called()
            self.assertIn("not empty", stderr.getvalue())

    def test_nca_uses_default_root_and_selected_virtual_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nca = root / "program.nca"
            keyset = root / "prod.keys"
            nca.write_bytes(b"nca")
            keyset.write_text("key", encoding="utf-8")

            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch("nsw_localize.cli.run_nstool") as mocked_run,
            ):
                self.assertEqual(
                    main(
                        [
                            "unpack",
                            "nca",
                            str(nca),
                            "--keyset",
                            str(keyset),
                            "--output",
                            str(root / "root"),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    main(
                        [
                            "unpack",
                            "nca",
                            str(nca),
                            "--keyset",
                            str(keyset),
                            "--output",
                            str(root / "partition"),
                            "--virtual-path",
                            "/0",
                        ]
                    ),
                    0,
                )

            self.assertEqual(mocked_run.call_args_list[0].args[1][3], "/")
            self.assertEqual(mocked_run.call_args_list[1].args[1][3], "/0")

    def test_missing_keyset_does_not_invoke_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nca = root / "program.nca"
            nca.write_bytes(b"nca")
            stderr = io.StringIO()

            with patch("nsw_localize.cli.run_nstool") as mocked_run, redirect_stderr(stderr):
                exit_code = main(
                    [
                        "unpack",
                        "nca",
                        str(nca),
                        "--keyset",
                        str(root / "missing.keys"),
                        "--output",
                        str(root / "out"),
                    ]
                )

            self.assertEqual(exit_code, 2)
            mocked_run.assert_not_called()
            self.assertIn("Keyset", stderr.getvalue())

    def test_process_failure_has_consistent_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "game.nsp"
            package.write_bytes(b"package")
            stderr = io.StringIO()

            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch(
                    "nsw_localize.cli.run_nstool",
                    side_effect=NstoolProcessError(
                        "NSTool NSP extraction failed with exit code 1: bad input"
                    ),
                ),
                redirect_stderr(stderr),
            ):
                exit_code = main(
                    ["unpack", "nsp", str(package), "--output", str(root / "out")]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("bad input", stderr.getvalue())

    def test_missing_executable_has_consistent_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "game.nsp"
            package.write_bytes(b"package")
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "unpack",
                        "nsp",
                        str(package),
                        "--output",
                        str(root / "out"),
                        "--nstool",
                        str(root / "missing-nstool"),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("--nstool", stderr.getvalue())

    def test_merge_nca_extracts_with_explicit_keyset_and_tik(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_nca = root / "base.nca"
            patch_nca = root / "patch.nca"
            keyset = root / "prod.keys"
            tik = root / "patch.tik"
            output = root / "romfs"

            base_nca.write_bytes(b"base")
            patch_nca.write_bytes(b"patch")
            keyset.write_text("keys", encoding="utf-8")
            tik.write_bytes(b"tik")

            stdout = io.StringIO()
            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch("nsw_localize.cli.run_nstool") as mocked_run,
                redirect_stdout(stdout),
            ):
                exit_code = main(
                    [
                        "merge-nca",
                        "--base",
                        str(base_nca),
                        "--patch",
                        str(patch_nca),
                        "--keyset",
                        str(keyset),
                        "--tik",
                        str(tik),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 0)
            mocked_run.assert_called_once()
            args = mocked_run.call_args[0][1]
            self.assertIn("--basenca", args)
            self.assertIn(str(base_nca.resolve()), args)
            self.assertIn("--tik", args)
            self.assertIn(str(tik.resolve()), args)
            self.assertIn("/1", args)
            self.assertIn("Extracted merged RomFS", stdout.getvalue())

    def test_merge_nca_uses_default_keyset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_nca = root / "base.nca"
            patch_nca = root / "patch.nca"
            default_keyset = root / "prod.keys"
            output = root / "romfs"

            base_nca.write_bytes(b"base")
            patch_nca.write_bytes(b"patch")
            default_keyset.write_text("keys", encoding="utf-8")

            stdout = io.StringIO()
            with (
                patch("nsw_localize.cli.resolve_nstool", return_value=Path("/tool/nstool")),
                patch("nsw_localize.cli.resolve_keyset", return_value=default_keyset.resolve()),
                patch("nsw_localize.cli.run_nstool") as mocked_run,
                redirect_stdout(stdout),
            ):
                exit_code = main(
                    [
                        "merge-nca",
                        "--base",
                        str(base_nca),
                        "--patch",
                        str(patch_nca),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 0)
            mocked_run.assert_called_once()
            args = mocked_run.call_args[0][1]
            self.assertIn(str(default_keyset.resolve()), args)

    def test_merge_nca_validates_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_nca = root / "base.nca"
            base_nca.write_bytes(b"base")
            stderr = io.StringIO()

            with patch("nsw_localize.cli.run_nstool") as mocked_run, redirect_stderr(stderr):
                exit_code = main(
                    [
                        "merge-nca",
                        "--base",
                        str(base_nca),
                        "--patch",
                        str(root / "missing.nca"),
                        "--output",
                        str(root / "romfs"),
                    ]
                )

            self.assertEqual(exit_code, 2)
            mocked_run.assert_not_called()
            self.assertIn("Patch NCA input", stderr.getvalue())

    def test_merge_nca_rejects_non_empty_output_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_nca = root / "base.nca"
            patch_nca = root / "patch.nca"
            keyset = root / "prod.keys"
            output = root / "romfs"
            output.mkdir()
            (output / "existing.txt").write_text("content", encoding="utf-8")

            base_nca.write_bytes(b"base")
            patch_nca.write_bytes(b"patch")
            keyset.write_text("keys", encoding="utf-8")

            stderr = io.StringIO()
            with patch("nsw_localize.cli.run_nstool") as mocked_run, redirect_stderr(stderr):
                exit_code = main(
                    [
                        "merge-nca",
                        "--base",
                        str(base_nca),
                        "--patch",
                        str(patch_nca),
                        "--keyset",
                        str(keyset),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 2)
            mocked_run.assert_not_called()
            self.assertIn("not empty", stderr.getvalue())

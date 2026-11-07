"""Command-line entry point for the NSTool wrapper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .nstool import (
    NstoolError,
    build_nca_extract_args,
    build_nca_merge_args,
    build_nsp_extract_args,
    prepare_output_directory,
    resolve_keyset,
    resolve_nstool,
    run_nstool,
    validate_input_file,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="nsl",
        description="Nintendo Switch Localization toolkit.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    # Subcommand: unpack
    unpack_parser = subcommands.add_parser(
        "unpack", help="Unpack Nintendo Switch NSP packages and NCA archives."
    )
    unpack_subcommands = unpack_parser.add_subparsers(dest="unpack_command", required=True)

    nsp_parser = unpack_subcommands.add_parser(
        "nsp", help="Extract the contents of an NSP package."
    )
    _add_common_options(nsp_parser)
    nsp_parser.add_argument("input", type=Path, help="Path to the .nsp package.")
    nsp_parser.set_defaults(handler=_extract_nsp)

    nca_parser = unpack_subcommands.add_parser(
        "nca", help="Extract a filesystem path from an NCA."
    )
    _add_common_options(nca_parser)
    nca_parser.add_argument("input", type=Path, help="Path to the .nca archive.")
    nca_parser.add_argument(
        "--keyset", required=True, type=Path, help="Path to prod.keys or another NSTool keyset."
    )
    nca_parser.add_argument(
        "--virtual-path",
        default="/",
        help="NCA path to extract, such as /0. Defaults to the archive root (/).",
    )
    nca_parser.set_defaults(handler=_extract_nca)

    # Top-level subcommand: merge-nca
    merge_parser = subcommands.add_parser(
        "merge-nca", help="Extract merged RomFS from a base NCA and an update NCA."
    )
    _add_common_options(merge_parser)
    merge_parser.add_argument(
        "--base", required=True, type=Path, help="Path to the base .nca archive."
    )
    merge_parser.add_argument(
        "--patch", required=True, type=Path, help="Path to the update .nca archive."
    )
    merge_parser.add_argument(
        "--keyset",
        type=Path,
        help="Path to prod.keys (defaults to ~/.switch/prod.keys if omitted).",
    )
    merge_parser.add_argument(
        "--tik",
        type=Path,
        help="Optional path to ticket file for title key decryption.",
    )
    merge_parser.set_defaults(handler=_extract_merged_nca)
    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, type=Path, help="Destination directory.")
    parser.add_argument(
        "--nstool",
        type=Path,
        help="Path to a compatible NSTool executable (defaults to ./nstool).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow NSTool to write into a non-empty output directory.",
    )


def _extract_nsp(arguments: argparse.Namespace) -> None:
    input_path = validate_input_file(arguments.input, "NSP input", ".nsp")
    executable = resolve_nstool(arguments.nstool)
    output_directory = prepare_output_directory(arguments.output, overwrite=arguments.overwrite)
    run_nstool(
        executable,
        build_nsp_extract_args(input_path, output_directory),
        operation="NSP extraction",
    )

    nca_paths = sorted(
        path
        for path in output_directory.rglob("*")
        if path.is_file() and path.suffix.lower() == ".nca"
    )
    print(f"Extracted NSP to {output_directory}")
    if nca_paths:
        print("Extracted NCA files:")
        for nca_path in nca_paths:
            print(nca_path)
    else:
        print("No NCA files were found in the extracted output.")


def _extract_nca(arguments: argparse.Namespace) -> None:
    input_path = validate_input_file(arguments.input, "NCA input", ".nca")
    keyset_path = validate_input_file(arguments.keyset, "Keyset")
    if not arguments.virtual_path.startswith("/"):
        raise NstoolError("NCA virtual path must start with '/'.")
    executable = resolve_nstool(arguments.nstool)
    output_directory = prepare_output_directory(arguments.output, overwrite=arguments.overwrite)
    run_nstool(
        executable,
        build_nca_extract_args(input_path, keyset_path, output_directory, arguments.virtual_path),
        operation="NCA extraction",
    )
    print(f"Extracted NCA path {arguments.virtual_path} to {output_directory}")


def _extract_merged_nca(arguments: argparse.Namespace) -> None:
    base_path = validate_input_file(arguments.base, "Base NCA input", ".nca")
    patch_path = validate_input_file(arguments.patch, "Patch NCA input", ".nca")
    keyset_path = resolve_keyset(arguments.keyset)
    tik_path = validate_input_file(arguments.tik, "Ticket") if arguments.tik is not None else None
    executable = resolve_nstool(arguments.nstool)
    output_directory = prepare_output_directory(arguments.output, overwrite=arguments.overwrite)
    run_nstool(
        executable,
        build_nca_merge_args(
            base_nca_path=base_path,
            patch_nca_path=patch_path,
            keyset_path=keyset_path,
            output_directory=output_directory,
            tik_path=tik_path,
        ),
        operation="Merged NCA extraction",
    )
    print(f"Extracted merged RomFS to {output_directory}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the command-line application."""
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        arguments.handler(arguments)
    except NstoolError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

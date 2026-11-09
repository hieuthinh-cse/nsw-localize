"""Command-line entry point for the NSTool wrapper."""

from __future__ import annotations

import argparse
import os
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
from .titlekeys import add_title_key, create_ephemeral_keyset, extract_ticket_entry


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

    nca_parser = unpack_subcommands.add_parser("nca", help="Extract a filesystem path from an NCA.")
    _add_common_options(nca_parser)
    nca_parser.add_argument("input", type=Path, help="Path to the .nca archive.")
    nca_parser.add_argument(
        "--keyset", required=True, type=Path, help="Path to prod.keys or another NSTool keyset."
    )
    nca_parser.add_argument(
        "--tik", type=Path, help="Optional ticket file providing title-key material."
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
        help="Compatibility alias for --patch-tik.",
    )
    merge_parser.add_argument("--base-tik", type=Path, help="Ticket for the base NCA title key.")
    merge_parser.add_argument("--patch-tik", type=Path, help="Ticket for the update NCA title key.")
    merge_parser.set_defaults(handler=_extract_merged_nca)

    add_title_key_parser = subcommands.add_parser(
        "add-title-key", help="Add a ticket's title key to a persistent title.keys file."
    )
    add_title_key_parser.add_argument("--tik", required=True, type=Path, help="Ticket file.")
    add_title_key_parser.add_argument(
        "--output",
        type=Path,
        help="Destination title.keys file (defaults to the user's .switch directory).",
    )
    add_title_key_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing entry with the same Rights ID if its key differs.",
    )
    add_title_key_parser.set_defaults(handler=_add_title_key)
    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, type=Path, help="Destination directory.")
    parser.add_argument(
        "--nstool",
        type=Path,
        help="Path to a compatible NSTool executable (defaults to ./nstool.exe on Windows, ./nstool on macOS/Linux).",
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
    tik_path = (
        validate_input_file(arguments.tik, "Ticket", ".tik") if arguments.tik is not None else None
    )
    if not arguments.virtual_path.startswith("/"):
        raise NstoolError("NCA virtual path must start with '/'.")
    executable = resolve_nstool(arguments.nstool)
    output_directory = prepare_output_directory(arguments.output, overwrite=arguments.overwrite)
    run_nstool(
        executable,
        build_nca_extract_args(
            input_path,
            keyset_path,
            output_directory,
            arguments.virtual_path,
            tik_path=tik_path,
        ),
        operation="NCA extraction",
    )
    print(f"Extracted NCA path {arguments.virtual_path} to {output_directory}")


def _extract_merged_nca(arguments: argparse.Namespace) -> None:
    base_path = validate_input_file(arguments.base, "Base NCA input", ".nca")
    patch_path = validate_input_file(arguments.patch, "Patch NCA input", ".nca")
    keyset_path = resolve_keyset(arguments.keyset)
    patch_tik = arguments.patch_tik or arguments.tik
    if arguments.patch_tik is not None and arguments.tik is not None:
        raise NstoolError("Use only one of --tik and --patch-tik.")
    base_tik = (
        validate_input_file(arguments.base_tik, "Base ticket")
        if arguments.base_tik is not None
        else None
    )
    patch_tik_path = (
        validate_input_file(patch_tik, "Patch ticket") if patch_tik is not None else None
    )
    executable = resolve_nstool(arguments.nstool)
    output_directory = prepare_output_directory(arguments.output, overwrite=arguments.overwrite)
    # Preserve the historical single-ticket/global-title.keys path.  Supplying both
    # tickets opts into deterministic, process-local preparation.
    if base_tik is None:
        run_nstool(
            executable,
            build_nca_merge_args(
                base_nca_path=base_path,
                patch_nca_path=patch_path,
                keyset_path=keyset_path,
                output_directory=output_directory,
                tik_path=patch_tik_path,
            ),
            operation="Merged NCA extraction",
        )
        print(f"Extracted merged RomFS to {output_directory}")
        return
    if patch_tik_path is None:
        raise NstoolError("--base-tik requires --patch-tik (or the compatibility alias --tik).")
    base_entry = extract_ticket_entry(base_tik, "Base ticket")
    patch_entry = extract_ticket_entry(patch_tik_path, "Patch ticket")
    temporary = create_ephemeral_keyset(keyset_path, [base_entry, patch_entry])
    try:
        environment = os.environ.copy()
        environment["HOME"] = temporary.name
        run_nstool(
            executable,
            build_nca_merge_args(
                base_nca_path=base_path,
                patch_nca_path=patch_path,
                keyset_path=Path(temporary.name) / keyset_path.name,
                output_directory=output_directory,
            ),
            operation="Merged NCA extraction",
            environment=environment,
        )
    finally:
        temporary.cleanup()
    print(f"Extracted merged RomFS to {output_directory}")


def _add_title_key(arguments: argparse.Namespace) -> None:
    ticket_path = validate_input_file(arguments.tik, "Ticket", ".tik")
    entry = extract_ticket_entry(ticket_path, "Ticket")
    destination, changed = add_title_key(entry, arguments.output, force=arguments.force)
    action = "Added" if changed else "Already present"
    print(f"{action} title key for Rights ID {entry.rights_id} in {destination}")


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

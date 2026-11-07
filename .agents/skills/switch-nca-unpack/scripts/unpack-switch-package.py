#!/usr/bin/env python3
"""Extract content files from a locally dumped Switch NSP or XCI."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


def existing_file(value: str) -> Path:
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    return path


def run(command: list[str]) -> None:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace", check=False)
    if result.returncode:
        diagnostic = "\n".join(line for line in result.stdout.splitlines()
                                if "failed to match key" not in line.lower())
        raise RuntimeError(f"{Path(command[0]).name} failed (exit {result.returncode}).\n{diagnostic}")


@contextmanager
def temporary_workspace(parent: Path):
    path = parent / f"switch_unpack_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input NSP or XCI")
    parser.add_argument("--prod-keys", required=True)
    parser.add_argument("--hactool", required=True)
    parser.add_argument("--output-directory")
    args = parser.parse_args()
    try:
        source = existing_file(args.input)
        keys = existing_file(args.prod_keys)
        hactool = existing_file(args.hactool)
        extension = source.suffix.lower()
        if extension not in {".nsp", ".xci"}:
            raise ValueError("Input must be an NSP or XCI.")
        output = Path(args.output_directory).expanduser().resolve() if args.output_directory else source.with_name(source.stem + " unpacked")
        if output.exists():
            raise ValueError(f"Output directory already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with temporary_workspace(output.parent) as temp_root:
            raw = temp_root / "raw"
            raw.mkdir()
            staged_output = temp_root / "output"
            staged_output.mkdir()
            container_type = "pfs0" if extension == ".nsp" else "xci"
            output_option = f"--outdir={raw}" if extension == ".nsp" else f"--securedir={raw}"
            run([str(hactool), "-k", str(keys), "--disablekeywarns", "-t", container_type,
                 output_option, str(source)])

            titlekey_arg: list[str] = []
            if extension == ".nsp":
                tickets = list(raw.glob("*.tik"))
                if not tickets:
                    raise RuntimeError("NSP contains no ticket (.tik).")
                ticket_data = tickets[0].read_bytes()
                if len(ticket_data) < 0x190:
                    raise RuntimeError("NSP ticket is too short to contain its title key.")
                titlekey_arg = [f"--titlekey={ticket_data[0x180:0x190].hex()}"]

            types = [("program", ["--romfsdir", "--exefsdir"]),
                     ("control", ["--romfsdir"]), ("manual", ["--romfsdir"]),
                     ("data", ["--romfsdir"])]
            ncas = sorted((p for p in raw.glob("*.nca") if not p.name.lower().endswith(".cnmt.nca")),
                          key=lambda p: p.stat().st_size, reverse=True)
            if not ncas:
                raise RuntimeError("No NCA files found in the package.")
            for nca in ncas:
                for content_type, options in types:
                    command = [str(hactool), "-k", str(keys), "--disablekeywarns", *titlekey_arg,
                               "-t", "nca", f"--xcontenttype={content_type}"]
                    for option in options:
                        folder = "legal" if content_type == "manual" else content_type
                        if option == "--exefsdir":
                            command.append(f"--exefsdir={staged_output / 'exefs'}")
                        else:
                            command.append(f"--romfsdir={staged_output / folder}")
                    command.append(str(nca))
                    # Different NCA content types are expected to be inapplicable;
                    # keep those diagnostics out of normal output, but retain valid files.
                    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            files = [p for p in staged_output.rglob("*") if p.is_file()]
            if not files:
                raise RuntimeError("No content was extracted. Check the keys; BKTR updates require the build-game-win skill.")
            staged_output.replace(output)
            print(f"Output: {output}\nFiles: {len(files)}\nRomFS: {(output / 'romfs').is_dir()}\nExeFS: {(output / 'exefs').is_dir()}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

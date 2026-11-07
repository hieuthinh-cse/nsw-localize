#!/usr/bin/env python3
"""Merge a matching Switch base/update NSP pair and copy out RomFS/game.win."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


def file_path(value: str) -> Path:
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    return path


def run(command: list[str]) -> str:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace", check=False)
    if result.returncode:
        # Older hactool builds can echo key names and values in warnings. Filter
        # those lines before preserving useful diagnostics for the caller.
        diagnostic = "\n".join(line for line in result.stdout.splitlines()
                                if "failed to match key" not in line.lower())
        detail = f"\n{diagnostic}" if diagnostic.strip() else ""
        raise RuntimeError(f"Command failed (exit {result.returncode}): {Path(command[0]).name}{detail}")
    return result.stdout


@contextmanager
def temporary_workspace(parent: Path):
    path = parent / f"build_game_win_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def extract_nsp(hactool: Path, nsp: Path, out: Path) -> list[Path]:
    out.mkdir(parents=True)
    run([str(hactool), "-t", "pfs0", f"--outdir={out}", "--disablekeywarns", str(nsp)])
    ncas = [p for p in out.glob("*.nca") if not p.name.lower().endswith(".cnmt.nca")]
    if not ncas:
        raise RuntimeError(f"No NCA files extracted from {nsp.name}")
    return ncas


def ticket_line(directory: Path) -> str:
    tickets = list(directory.glob("*.tik"))
    if not tickets:
        raise RuntimeError(f"No ticket found in {directory.name}")
    ticket = tickets[0]
    data = ticket.read_bytes()
    if len(data) < 0x190:
        raise RuntimeError(f"Ticket is too short: {ticket.name}")
    rights_id = ticket.stem
    title_key = data[0x180:0x190].hex()
    return f"{rights_id} = {title_key}"


def ticket_title_id(directory: Path) -> int:
    tickets = list(directory.glob("*.tik"))
    if not tickets:
        raise RuntimeError(f"No ticket found in {directory.name}")
    match = re.match(r"([0-9a-fA-F]{16})", tickets[0].stem)
    if not match:
        raise RuntimeError(f"Ticket name has no 16-digit title ID: {tickets[0].name}")
    return int(match.group(1), 16)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--base-nsp")
    source.add_argument("--base-nca")
    parser.add_argument("--update-nsp")
    parser.add_argument("--update-nca")
    parser.add_argument("--prod-keys", required=True)
    parser.add_argument("--title-keys", help="Required with --base-nca/--update-nca")
    parser.add_argument("--hactoolnet", required=True)
    parser.add_argument("--hactool", help="Required with NSP inputs")
    parser.add_argument("--output-directory", required=True)
    args = parser.parse_args()

    try:
        keys = file_path(args.prod_keys)
        hactoolnet = file_path(args.hactoolnet)
        output = Path(args.output_directory).expanduser().resolve()
        if output.exists():
            raise ValueError(f"Output already exists: {output}")
        nsp_mode = args.base_nsp is not None
        if nsp_mode != (args.update_nsp is not None):
            raise ValueError("Provide both --base-nsp and --update-nsp, or use the NCA pair.")
        if not nsp_mode and (args.update_nca is None or args.title_keys is None):
            raise ValueError("NCA mode requires --update-nca and --title-keys.")
        if nsp_mode and (args.update_nca is not None or args.title_keys is not None):
            raise ValueError("Do not mix NSP and NCA inputs.")

        output.parent.mkdir(parents=True, exist_ok=True)
        with temporary_workspace(output.parent) as root:
            if nsp_mode:
                if not args.hactool:
                    raise ValueError("--hactool is required for NSP inputs.")
                hactool = file_path(args.hactool)
                base_nsp, update_nsp = file_path(args.base_nsp), file_path(args.update_nsp)
                base_dir, update_dir = root / "base", root / "update"
                base_ncas = extract_nsp(hactool, base_nsp, base_dir)
                update_ncas = extract_nsp(hactool, update_nsp, update_dir)
                if ticket_title_id(update_dir) != ticket_title_id(base_dir) + 0x800:
                    raise ValueError("Base and update ticket title IDs do not identify a matching game/update pair.")
                base_nca = max(base_ncas, key=lambda p: p.stat().st_size)
                update_nca = max(update_ncas, key=lambda p: p.stat().st_size)
                title_keys = root / "title.keys"
                title_keys.write_text("\n".join((ticket_line(base_dir), ticket_line(update_dir))) + "\n", encoding="ascii")
                base_label, update_label = base_nsp.name, update_nsp.name
            else:
                base_nca, update_nca = file_path(args.base_nca), file_path(args.update_nca)
                title_keys = file_path(args.title_keys)
                base_label, update_label = base_nca.name, update_nca.name

            merged = root / "merged-romfs"
            merged.mkdir()
            merge_log = run([str(hactoolnet), "-k", str(keys), "--titlekeys", str(title_keys), "-t", "nca",
                             "--basenca", str(base_nca), "--romfsdir", str(merged), str(update_nca)])
            game_win = merged / "game.win"
            if not game_win.is_file():
                entries = [f"{p.relative_to(merged)} ({p.stat().st_size} bytes)" for p in merged.rglob("*") if p.is_file()]
                safe_log = "\n".join(line for line in merge_log.splitlines()
                                      if "failed to match key" not in line.lower())
                details = "; ".join(entries) if entries else "no files were emitted"
                if safe_log.strip():
                    details += f"\nhactoolnet: {safe_log}"
                raise RuntimeError(f"Merged RomFS does not contain game.win: {details}")
            output.mkdir(parents=True)
            destination = output / "game.win"
            shutil.copy2(game_win, destination)
            digest_state = hashlib.sha256()
            with destination.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest_state.update(chunk)
            digest = digest_state.hexdigest()
            print(f"Base: {base_label}\nUpdate: {update_label}\nOutput: {destination}\n"
                  f"Bytes: {destination.stat().st_size}\nSHA256: {digest}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

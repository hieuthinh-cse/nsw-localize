"""Secret-safe title-key extraction and ephemeral keyset helpers."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .nstool import ValidationError, validate_input_file

_HEX = re.compile(r"^[0-9a-fA-F]+$")
_RIGHTS_ID_OFFSET = 0x2A0
_TITLE_KEY_OFFSET = 0x180
_KEY_LINE = re.compile(r"^\s*([0-9a-fA-F]{32})\s*=\s*([0-9a-fA-F]{32})\s*$")


@dataclass(frozen=True)
class TitleKeyEntry:
    rights_id: str
    title_key: str


def _validate_hex(value: bytes, length: int, label: str) -> str:
    if len(value) != length or not _HEX.fullmatch(value.hex()):
        raise ValidationError(f"{label} does not contain usable title-key data")
    return value.hex().upper()


def extract_ticket_entry(ticket_path: Path, label: str = "Ticket") -> TitleKeyEntry:
    """Read the rights ID and encrypted title key from a ticket without logging values."""
    ticket = validate_input_file(ticket_path, label, ".tik")
    data = ticket.read_bytes()
    end = max(_RIGHTS_ID_OFFSET + 16, _TITLE_KEY_OFFSET + 16)
    if len(data) < end:
        raise ValidationError(f"{label} is malformed or does not contain usable title-key data")
    rights_id = _validate_hex(data[_RIGHTS_ID_OFFSET : _RIGHTS_ID_OFFSET + 16], 16, label)
    title_key = _validate_hex(data[_TITLE_KEY_OFFSET : _TITLE_KEY_OFFSET + 16], 16, label)
    return TitleKeyEntry(rights_id, title_key)


def merge_title_key_entries(entries: Iterable[TitleKeyEntry]) -> list[TitleKeyEntry]:
    """Deduplicate matching entries and reject conflicting rights IDs."""
    merged: dict[str, TitleKeyEntry] = {}
    for entry in entries:
        previous = merged.get(entry.rights_id)
        if previous is not None and previous.title_key != entry.title_key:
            raise ValidationError(f"Conflicting title-key entries for Rights ID {entry.rights_id}")
        merged[entry.rights_id] = entry
    return list(merged.values())


def create_ephemeral_keyset(
    keyset_path: Path, entries: Iterable[TitleKeyEntry]
) -> tempfile.TemporaryDirectory[str]:
    """Copy the keyset and append title-key entries in a disposable directory."""
    merged = merge_title_key_entries(entries)
    if not merged:
        raise ValidationError("No usable title-key entries were provided")
    source = validate_input_file(keyset_path, "Keyset")
    temporary = tempfile.TemporaryDirectory(prefix="nsl-keys-")
    target = Path(temporary.name) / source.name
    target.write_bytes(source.read_bytes())
    title_keys = Path(temporary.name) / "title.keys"
    with title_keys.open("w", encoding="utf-8") as handle:
        for entry in merged:
            handle.write(f"{entry.rights_id} = {entry.title_key}\n")
    switch_dir = Path(temporary.name) / ".switch"
    switch_dir.mkdir()
    (switch_dir / "title.keys").write_bytes(title_keys.read_bytes())
    return temporary


def title_key_metadata(entries: Iterable[TitleKeyEntry]) -> str:
    """Return safe metadata suitable for diagnostics."""
    return ", ".join(entry.rights_id for entry in entries)


def default_title_keys_path(home: Optional[Path] = None) -> Path:
    """Return the user's platform-neutral Switch title-key path."""
    return (home or Path.home()) / ".switch" / "title.keys"


def _read_persistent_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    if not path.is_file():
        raise ValidationError(f"Title-key file must be a regular file: {path}")
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ValidationError(f"Unable to read title-key file: {path}") from error


def _merge_persistent_entry(
    lines: list[str], entry: TitleKeyEntry, *, force: bool
) -> tuple[list[str], bool]:
    result: list[str] = []
    found = False
    changed = False
    for line in lines:
        match = _KEY_LINE.fullmatch(line)
        if match is None:
            result.append(line)
            continue
        rights_id, title_key = match.group(1).upper(), match.group(2).upper()
        if rights_id != entry.rights_id:
            result.append(line)
            continue
        found = True
        if title_key == entry.title_key:
            result.append(f"{entry.rights_id} = {entry.title_key}")
            continue
        if not force:
            raise ValidationError(f"Conflicting title-key entry for Rights ID {entry.rights_id}")
        result.append(f"{entry.rights_id} = {entry.title_key}")
        changed = True
    if not found:
        if result and result[-1] != "":
            result.append("")
        result.append(f"{entry.rights_id} = {entry.title_key}")
        changed = True
    return result, changed


def add_title_key(
    entry: TitleKeyEntry,
    output_path: Optional[Path] = None,
    *,
    force: bool = False,
) -> tuple[Path, bool]:
    """Persist one title-key entry without exposing its value in diagnostics."""
    destination = (output_path or default_title_keys_path()).expanduser()
    lines = _read_persistent_lines(destination)
    merged, changed = _merge_persistent_entry(lines, entry, force=force)
    if not changed:
        return destination, False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write("\n".join(merged) + "\n")
        temporary_path.replace(destination)
    except (OSError, UnicodeError) as error:
        raise ValidationError(f"Unable to write title-key file: {destination}") from error
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination, True

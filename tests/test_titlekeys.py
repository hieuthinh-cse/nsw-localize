from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nsw_localize.nstool import ValidationError
from nsw_localize.titlekeys import (
    TitleKeyEntry,
    add_title_key,
    create_ephemeral_keyset,
    default_title_keys_path,
    extract_ticket_entry,
    merge_title_key_entries,
)


class TitleKeyTests(unittest.TestCase):
    def _ticket(self, root: Path, name: str, rights: bytes, key: bytes) -> Path:
        data = bytearray(0x2B0)
        data[0x2A0 : 0x2A0 + 16] = rights
        data[0x180 : 0x180 + 16] = key
        path = root / name
        path.write_bytes(data)
        return path

    def test_extracts_synthetic_ticket_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = extract_ticket_entry(self._ticket(root, "base.tik", b"B" * 16, b"K" * 16))
            self.assertEqual(entry.rights_id, (b"B" * 16).hex().upper())
            self.assertEqual(entry.title_key, (b"K" * 16).hex().upper())

    def test_rejects_conflicting_duplicate(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Conflicting"):
            merge_title_key_entries([TitleKeyEntry("A", "1"), TitleKeyEntry("A", "2")])

    def test_ephemeral_keyset_is_cleaned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "prod.keys"
            source.write_text("master_key = safe\n", encoding="utf-8")
            temporary = create_ephemeral_keyset(source, [TitleKeyEntry("A" * 32, "B" * 32)])
            path = Path(temporary.name) / "title.keys"
            self.assertIn("A" * 32, path.read_text(encoding="utf-8"))
            temporary.cleanup()
            self.assertFalse(path.exists())
            self.assertEqual(source.read_text(encoding="utf-8"), "master_key = safe\n")

    def test_default_title_key_path_uses_supplied_home(self) -> None:
        self.assertEqual(
            default_title_keys_path(Path("C:/Users/tester")),
            Path("C:/Users/tester") / ".switch" / "title.keys",
        )

    def test_add_title_key_preserves_unrelated_lines_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".switch" / "title.keys"
            path.parent.mkdir()
            path.write_text(
                "master_key = safe\n" + "A" * 32 + " = " + "B" * 32 + "\n", encoding="utf-8"
            )
            entry = TitleKeyEntry("C" * 32, "D" * 32)
            destination, changed = add_title_key(entry, path)
            self.assertEqual(destination, path)
            self.assertTrue(changed)
            first = path.read_text(encoding="utf-8")
            self.assertIn("master_key = safe", first)
            self.assertEqual(first.count("C" * 32), 1)
            _, changed_again = add_title_key(entry, path)
            self.assertFalse(changed_again)
            self.assertEqual(path.read_text(encoding="utf-8"), first)

    def test_conflict_does_not_change_file_and_force_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "title.keys"
            path.write_text("A" * 32 + " = " + "B" * 32 + "\n", encoding="utf-8")
            entry = TitleKeyEntry("A" * 32, "C" * 32)
            original = path.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "Conflicting"):
                add_title_key(entry, path)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            add_title_key(entry, path, force=True)
            self.assertIn("A" * 32 + " = " + "C" * 32, path.read_text(encoding="utf-8"))

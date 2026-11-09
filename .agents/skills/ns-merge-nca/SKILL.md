---
name: ns-merge-nca
description: Merge a Nintendo Switch base package and update package (or their Program NCAs) to extract a complete patched RomFS (and isolate game.win for GameMaker) using the nsl CLI.
---

# Merge Switch NCAs (RomFS / game.win)

Use this skill to combine a Nintendo Switch base game and its update patch (BKTR layout) into a unified, fully patched RomFS partition (`/1`), or to extract `game.win` for GameMaker localization.

> [!IMPORTANT]
> Always execute operations via `uv run nsl` or `.venv/bin/nsl`. Do not invoke underlying binary engines directly.

## Workflow

### 1. Extract NSPs (if inputs are packages)
If the user provides `.nsp` packages instead of extracted `.nca` files, unpack both using the `ns-unpack` skill:

```sh
uv run nsl unpack nsp "path/to/base.nsp" --output extracted/base_nsp
uv run nsl unpack nsp "path/to/update.nsp" --output extracted/update_nsp
```

Identify the Program NCA from each package:
- Select the largest `.nca` file from each folder (ignoring `.cnmt.nca`).
- If a ticket file (`.tik`) exists in `extracted/update_nsp/`, note its path.

### 2. Merge Base and Update NCAs
Execute `nsl merge-nca` to layer the BKTR update over the base Program NCA:

```sh
uv run nsl merge-nca \
  --base "extracted/base_nsp/<base_program>.nca" \
  --patch "extracted/update_nsp/<update_program>.nca" \
  --output "extracted/merged_romfs"
```

**Optional Flags:**
- `--keyset "path/to/prod.keys"`: Specify keyset path (defaults automatically to `~/.switch/prod.keys` if omitted).
- `--base-tik "extracted/base_nsp/<ticket>.tik"`: Ticket supplying the base NCA title key.
- `--patch-tik "extracted/update_nsp/<ticket>.tik"`: Ticket supplying the update NCA title key. The CLI creates a secure temporary combined keyset and removes it after the run.
- `--tik "extracted/update_nsp/<ticket>.tik"`: Compatibility alias for `--patch-tik` when base title-key discovery is already configured.
- `--overwrite`: Permit writing into an existing non-empty directory.

The result in `extracted/merged_romfs` contains the complete, merged RomFS directory structure.

### 3. GameMaker Localization (`game.win`)
For GameMaker games, the compiled game data is stored at `game.win` in the root of the RomFS:

1. Verify `extracted/merged_romfs/game.win` exists.
2. If isolating `game.win` for translation or analysis:
   ```sh
   cp "extracted/merged_romfs/game.win" "destination/game.win"
   ```
3. Report the output path, byte size, and SHA-256 digest of `game.win`.

## Constraints & Diagnostics

- **BKTR Updates:** An update Program NCA cannot be extracted standalone; it must be merged against its matching base Program NCA.
- **Mismatches:** If the merge fails with layout or title key errors, verify that the base and update NSPs correspond to the exact same Title ID (Update Title ID is typically Base Title ID + 0x800).
- **Key Material:** Keep `prod.keys`, `title.keys`, and ticket hex keys out of logs, commits, and user-facing output.

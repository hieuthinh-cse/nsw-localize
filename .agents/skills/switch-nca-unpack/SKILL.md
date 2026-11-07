---
name: switch-nca-unpack
description: Extract RomFS, ExeFS, and auxiliary content from personally dumped Nintendo Switch NSP/XCI files with hactool, including ticket titlekeys. Use build-game-win to merge BKTR updates.
---

# Switch NCA Unpack

Use this skill for locally dumped Nintendo Switch content that the user owns or is authorized to inspect. It prepares files for localization or asset analysis; it does not distribute keys or game content.

## Workflow

1. Confirm the requested input location. By default, output is a new `"<package name> unpacked"` folder beside the NSP/XCI; do not overwrite an existing output directory.
2. Use `scripts/unpack-switch-package.py` for NSP/XCI input with Python 3. Supply the bundled `tools/hactool.exe` and a local `prod.keys` file. It extracts the container and, for NSP, reads the title key from the included ticket without printing it.
3. Keep `prod.keys`, `title.keys`, tickets, and derived titlekeys out of command output, committed files, and final responses.
4. Inspect the output and state separately which content types were actually extracted.

## Update patches (BKTR)

An update Program NCA may report `Invalid BKTR layout` when extracted by itself. It is a patch that needs the matching Program NCA from the base game. For a complete merged RomFS and `game.win`, use the `build-game-win` skill, which merges through hactoolnet/LibHac.

Control and legal NCAs can still extract from an update NSP even when its Program RomFS/ExeFS cannot. Do not represent that partial result as a complete game extraction.

## Script

Run from the project root, adjusting paths as necessary:

```sh
python .agents/skills/switch-nca-unpack/scripts/unpack-switch-package.py \
  --input ./game.nsp \
  --prod-keys ./.agents/skills/switch-nca-unpack/keys/prod.keys \
  --hactool ./.agents/skills/switch-nca-unpack/tools/hactool.exe
```

Override `--output-directory`, `--prod-keys`, or `--hactool` as needed. This extractor does not merge BKTR updates.

---
name: build-game-win
description: Merge a Nintendo Switch base NSP and update NSP into a complete patched RomFS and extract game.win for GameMaker analysis or localization. Use when a BKTR update must be combined with its matching base; do not use for repacking NSPs or editing game.win contents.
---

# Build game.win

Use this skill only with a user-owned or authorized dump. The output is a local analysis artifact; it does not rebuild or install an NSP.

## Workflow

1. Identify the matching base game NSP/update NSP (or their already-extracted Program NCAs), `prod.keys`, and `hactoolnet`/LibHac. Do not mix title IDs or update versions.
2. If the inputs are NSPs, use any PFS0/NSP extractor (the bundled script uses `hactool`) to obtain the Program NCAs. If Program NCAs are already available, no `hactool` step is needed. Select the largest non-`.cnmt.nca` NCA from each package as the Program NCA.
3. Read each NSP's ticket title key into a temporary `title.keys` file. Keep tickets, title keys, and key material out of logs, reports, and the repository.
4. Run hactoolnet against the update Program NCA with the matching base Program NCA supplied through `--basenca`, and write a merged RomFS directory.
5. Copy only the merged `romfs/game.win` to a new output path. Preserve the original NSPs and any existing mod files.
6. Report output path, byte size, SHA-256, and which base/update versions were used.

## Important constraints

- A BKTR update is not independently extractable as a complete RomFS; it must be layered over the matching base Program NCA/RomFS.
- Prefer hactoolnet/LibHac for the BKTR merge. Older hactool builds can fail with `Invalid BKTR layout` even when the dump is valid.
- Never overwrite an existing `game.win`; require a new output directory or an explicit, verified destination.
- If the merge fails, retain the diagnostic error but do not claim a complete extraction. Common causes are a mismatched base, wrong title key, missing key generation, or an old extractor.

For the repeatable NSP implementation, run [scripts/build-game-win.py](scripts/build-game-win.py) with Python 3. It uses `hactool` only for NSP container extraction; the BKTR merge is performed by `hactoolnet`.

```sh
python .agents/skills/build-game-win/scripts/build-game-win.py \
  --base-nsp 'path/to/base.nsp' \
  --update-nsp 'path/to/update.nsp' \
  --prod-keys 'path/to/prod.keys' \
  --hactoolnet 'path/to/hactoolnet.exe' \
  --hactool 'path/to/hactool.exe' \
  --output-directory 'path/to/new-output'
```

---
name: ns-unpack
description: Extract Nintendo Switch NSP packages into NCAs, and extract RomFS (/1) or ExeFS (/0) partitions from Program NCAs using the nsl CLI. Use ns-merge-nca to merge BKTR updates.
---

# Switch Package and NCA Unpack

Use this skill for locally dumped Nintendo Switch content that the user owns or is authorized to inspect. It prepares files for localization and asset analysis using the project CLI (`nsl`).

> [!IMPORTANT]
> Always execute operations via `uv run nsl` or `.venv/bin/nsl`. Do not invoke underlying binary engines directly.

## Workflow

### 1. Extract NSP Container
Unpack the `.nsp` file into its constituent `.nca` archives and ticket files:

```sh
uv run nsl unpack nsp "path/to/game.nsp" --output extracted/nsp_out
```

The command extracts the package files and lists all extracted NCAs (Program, Control, Manual, Metadata).

### 2. Extract NCA Partition (RomFS / ExeFS)
Locate the Program NCA (typically the largest `.nca` file, excluding `.cnmt.nca`) and extract the desired partition:

- **Extract RomFS (`/1`):**
  ```sh
  uv run nsl unpack nca "extracted/nsp_out/<program>.nca" \
    --keyset "path/to/prod.keys" \
    --virtual-path /1 \
    --output extracted/romfs
  ```

- **Extract ExeFS (`/0`):**
  ```sh
  uv run nsl unpack nca "extracted/nsp_out/<program>.nca" \
    --keyset "path/to/prod.keys" \
    --virtual-path /0 \
    --output extracted/exefs
  ```

Add `--overwrite` if writing into an existing directory.

## Update Patches (BKTR)

An update Program NCA cannot be unpacked on its own because it contains delta-compressed BKTR sections layered over the base game.

If you are working with an update patch or need a merged RomFS with all updates applied, use the **`ns-merge-nca`** skill (`uv run nsl merge-nca`), which merges the base Program NCA and update Program NCA together.

## Security Constraints

- Keep `prod.keys`, `title.keys`, tickets, and derived key material out of commit history, logs, and final user responses.
- Ensure `title.keys` (if required for eShop dumps) is present in `~/.switch/` or accessible to the keyset.

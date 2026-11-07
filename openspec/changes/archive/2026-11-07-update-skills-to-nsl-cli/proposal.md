# Proposal

## Why

The current agent skills (`switch-nca-unpack` and `build-game-win`) rely on obsolete Python scripts that invoke bundled Windows binaries (`hactool.exe` and `hactoolnet.exe`). This violates the project policy documented in `AGENTS.md` and repository standards, which mandate using the unified `nsl` CLI (`uv run nsl`). Updating and renaming the skills to `ns-unpack` and `ns-merge-nca` aligns agent workflows with the current CLI tooling and eliminates unmaintained legacy helper scripts and external binaries.

## What Changes

- Rename skill `switch-nca-unpack` to `ns-unpack` under `.agents/skills/ns-unpack/`.
- Rewrite `ns-unpack/SKILL.md` to instruct agents to use `uv run nsl unpack nsp` and `uv run nsl unpack nca` for RomFS (`/1`) and ExeFS (`/0`) extraction.
- Remove bundled `tools/hactool.exe` and `scripts/unpack-switch-package.py` from `ns-unpack`.
- Rename skill `build-game-win` to `ns-merge-nca` under `.agents/skills/ns-merge-nca/`.
- Rewrite `ns-merge-nca/SKILL.md` to instruct agents to use `uv run nsl unpack nsp` (when starting from NSPs) and `uv run nsl merge-nca` for RomFS and `game.win` extraction.
- Remove legacy `scripts/build-game-win.py`.
- Update `.gitignore` to reference `.agents/skills/ns-unpack/keys/` instead of `switch-nca-unpack`.

## Capabilities

### New Capabilities
- `agent-skills`: Standardized agent workflows for Nintendo Switch package unpacking (`ns-unpack`) and merged RomFS/game.win extraction (`ns-merge-nca`) via the `nsl` CLI.

### Modified Capabilities
*(None. The core CLI capabilities under `switch-content-unpacking` remain unchanged.)*

## Impact

- Agents invoking unpacking and merging skills will run standardized `nsl` CLI commands instead of legacy Python scripts or direct binary invocations.
- Removed legacy binaries (`hactool.exe`) and scripts reduce repository maintenance overhead and platform-specific dependencies.
- No breaking changes to the `nsl` CLI itself.

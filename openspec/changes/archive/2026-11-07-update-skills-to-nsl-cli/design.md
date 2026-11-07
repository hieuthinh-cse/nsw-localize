# Design

## Context

See proposal.md for motivation. The project currently has two agent skills (`switch-nca-unpack` and `build-game-win`) located in `.agents/skills/`. Both skills rely on obsolete Python driver scripts and bundled Windows executables (`hactool.exe` and `hactoolnet.exe`). Meanwhile, the repository contains a fully tested and supported Python CLI package (`nsl`) providing `unpack nsp`, `unpack nca`, and `merge-nca` commands, powered by platform-aware `nstool` resolution.

## Goals / Non-Goals

**Goals:**
- Migrate agent workflows to invoke `uv run nsl` exclusively for package unpacking and NCA merging.
- Rename `.agents/skills/switch-nca-unpack` to `.agents/skills/ns-unpack` and update frontmatter/instructions.
- Rename `.agents/skills/build-game-win` to `.agents/skills/ns-merge-nca` and generalize instructions to RomFS merging with `game.win` extraction support.
- Delete obsolete helper scripts (`unpack-switch-package.py`, `build-game-win.py`) and bundled binary (`tools/hactool.exe`).
- Update repo configuration (`.gitignore`) and cross-references.

**Non-Goals:**
- Modifying `src/nsw_localize/` or core CLI implementation.
- Maintaining backward-compatible aliases for legacy skill names once renamed.

## Decisions

### 1. Pure CLI guidance in SKILL.md vs. Python wrapper scripts
- **Decision:** Document sequential `uv run nsl` commands directly in each `SKILL.md` rather than providing intermediate Python wrapper scripts.
- **Rationale:** Intermediate scripts introduce duplicate argument parsing, maintenance overhead, and risk drifting from CLI updates. Standardized CLI commands are already self-contained and clear for agents to execute.
- **Alternatives considered:** Keeping rewritten Python scripts in `scripts/`. Rejected as unnecessary wrapper layers.

### 2. Generalizing `build-game-win` to `ns-merge-nca`
- **Decision:** Rename the skill to `ns-merge-nca` to reflect the CLI command `nsl merge-nca`. Maintain documentation for `game.win` isolation as a specialized step within the RomFS merge workflow.
- **Rationale:** Merging base and update NCAs is a general Switch RomFS operation needed for any title with BKTR updates, not just GameMaker titles.
- **Alternatives considered:** Keeping the skill name `build-game-win` or creating two separate merge skills. Rejected to keep the skill set minimal and aligned with `nsl` commands.

### 3. Removal of bundled external binaries
- **Decision:** Delete `.agents/skills/switch-nca-unpack/tools/hactool.exe` and clean up tool directories.
- **Rationale:** `nsl` uses `nstool` binaries located in the workspace root or PATH. Bundling extraneous binaries in skill directories violates project rules and bloats the repository.

## Risks / Trade-offs

- **[Risk] Existing documentation or instructions referencing old skill names:**
  → *Mitigation:* Perform a full repository grep for `switch-nca-unpack` and `build-game-win` to update all occurrences (including `.gitignore`).

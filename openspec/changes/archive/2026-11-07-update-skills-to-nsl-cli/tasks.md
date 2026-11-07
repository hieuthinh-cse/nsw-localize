# Tasks

## 1. Skill Restructuring and Cleanup

- [x] 1.1 Move `.agents/skills/switch-nca-unpack` to `.agents/skills/ns-unpack` and delete `tools/hactool.exe` and `scripts/unpack-switch-package.py`. Verify old directory is gone and no binary files remain.
- [x] 1.2 Move `.agents/skills/build-game-win` to `.agents/skills/ns-merge-nca` and delete `scripts/build-game-win.py`. Verify old directory and obsolete scripts are removed.

## 2. Skill Documentation Authoring

- [x] 2.1 Rewrite `.agents/skills/ns-unpack/SKILL.md` with name `ns-unpack`, updated description, and step-by-step guidance for `uv run nsl unpack nsp` and `uv run nsl unpack nca`, cross-referencing `ns-merge-nca` for BKTR updates. Verify commands match CLI options.
- [x] 2.2 Rewrite `.agents/skills/ns-merge-nca/SKILL.md` with name `ns-merge-nca`, updated description, and step-by-step guidance for `uv run nsl merge-nca` (with NSP preparation and ticket handling) and GameMaker `game.win` extraction. Verify commands match CLI options.

## 3. Configuration and Reference Consistency

- [x] 3.1 Update `.gitignore` to replace `.agents/skills/switch-nca-unpack/keys/` with `.agents/skills/ns-unpack/keys/`. Verify git status reflects the updated ignore pattern.
- [x] 3.2 Audit repository references to ensure no dangling mentions of `switch-nca-unpack` or `build-game-win` remain. Verify via `git grep`.

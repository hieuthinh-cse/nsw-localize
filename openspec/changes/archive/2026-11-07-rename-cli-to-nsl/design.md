# Design

## Context

Currently, `nsw_localize.cli` exposes a flat `ArgumentParser` with `nsp`, `nca`, and `merge-nca` commands, registered under `nsw-unpack` in `pyproject.toml`. As the toolkit expands into broader localization workflows, a concise root binary name (`nsl`) and clean subcommand grouping are needed. Unpacking commands (`nsp`, `nca`) belong under `unpack`, while `merge-nca` operates as a dedicated top-level command (`nsl merge-nca`).

See `proposal.md` for background motivation.

## Goals / Non-Goals

**Goals:**
- Provide `nsl` as the sole CLI executable installed via `pyproject.toml`.
- Group raw package and archive extraction under the `unpack` subcommand:
  - `nsl unpack nsp`
  - `nsl unpack nca`
- Expose `merge-nca` directly as a top-level subcommand:
  - `nsl merge-nca`
- Update documentation (`README.md`, `AGENTS.md`) and references in `.agents/skills/` to use `nsl unpack` and `nsl merge-nca`.

**Non-Goals:**
- Support backward-compatibility aliases or legacy command redirection (no `nsw-unpack` script or deprecated root commands).
- Modify underlying `nstool.py` invocation logic or extraction argument handling.
- Change command flag names or behaviors (`--output`, `--keyset`, `--virtual-path`, `--base`, `--patch`, `--tik`).

## Decisions

### Decision 1: Subparser architecture
- **Choice**:
  - Root parser (`prog="nsl"`) creates top-level subparsers (`dest="command"`).
  - Subcommands at root:
    - `unpack`: creates nested subparsers (`dest="unpack_command"`) for `nsp` and `nca`.
    - `merge-nca`: direct root command handling merged RomFS extraction from base and update NCAs.
- **Rationale**:
  - `nsp` and `nca` are unpacking operations on individual packages/archives.
  - `merge-nca` is a distinct RomFS reconstruction workflow merging two archives.
  - Clear separation avoids overly deep nesting while keeping operations logically organized.

### Decision 2: Clean cut without backward compatibility
- **Choice**: Remove `nsw-unpack` entirely from `pyproject.toml` and omit fallback argument shims in `src/nsw_localize/cli.py`.
- **Rationale**: The project is in early development with a small user and test base; avoiding legacy baggage keeps the CLI codebase lean and maintainable.

## Risks / Trade-offs

- **[Risk] Existing scripts or documentation referencing `nsw-unpack` will fail immediately**:
  - *Mitigation*: Update all repo references (`AGENTS.md`, `README.md`, `.agents/skills/`) as part of this change.

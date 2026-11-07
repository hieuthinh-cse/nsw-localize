# Proposal

## Why

The current CLI entry point `nsw-unpack` is verbose and tightly coupled to unpacking, while the project scope is broader (`nsw-localize`). Renaming the base executable to `nsl` provides a concise root CLI and clean subcommand organization: nested extraction commands for packages and raw archives (`nsl unpack nsp`, `nsl unpack nca`), and direct top-level commands for dedicated workflows like `nsl merge-nca`.

## What Changes

- **BREAKING**: Replace `nsw-unpack` with `nsl` as the console script in `pyproject.toml`. No backward-compatibility alias is retained.
- **BREAKING**: Restructure CLI subcommands:
  - `nsl unpack nsp <input> --output <dir>`
  - `nsl unpack nca <input> --keyset <path> --output <dir> [--virtual-path <path>]`
  - `nsl merge-nca --base <base> --patch <patch> --output <dir> [--keyset <path>] [--tik <path>]` (top-level subcommand, without `unpack` prefix)
- Update CLI parser (`src/nsw_localize/cli.py`) with root subcommands `unpack` (nested `nsp`, `nca`) and `merge-nca`.
- Update project documentation and agent instructions (`README.md`, `AGENTS.md`, and skill references) to use `nsl unpack nsp`, `nsl unpack nca`, and `nsl merge-nca`.
- Update CLI test suites to test the new parser structure and command invocations.

## Capabilities

### Modified Capabilities
- `switch-content-unpacking`: Updates the command-line interface specification to use the `nsl` base executable with `nsl unpack nsp`, `nsl unpack nca`, and top-level `nsl merge-nca`.

## Impact

- CLI entry points: `[project.scripts]` in `pyproject.toml` defines only `nsl = "nsw_localize.cli:main"`.
- Command invocations in scripts, CI, and agent guidelines (`AGENTS.md`, skills) change from `uv run nsw-unpack ...` to `uv run nsl unpack nsp ...`, `uv run nsl unpack nca ...`, and `uv run nsl merge-nca ...`.
- Automated test suites are updated to match the new command structure.

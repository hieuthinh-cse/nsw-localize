# Design

## Context

See [proposal.md](proposal.md) for motivation and the `switch-content-unpacking` spec for the behavior contract. The repository currently has an executable `nstool` and only a Rust “Hello, world!” source file; it has no Python packaging, command interface, or automated test suite. `nstool` accepts a keyset with `-k` and extracts PFS0/NSP or NCA virtual paths with `-x`.

## Goals / Non-Goals

**Goals:**

- Deliver a small `uv`-managed Python distribution with predictable `nsp` and `nca` subcommands.
- Keep all external execution explicit, path-safe, and straightforward to unit test without Nintendo content or keys.
- Make the local `nstool` executable the default while permitting an explicit alternate binary.

**Non-Goals:**

- Implement decryption, NSP/NCA parsing, update merging, game text extraction, translation, or LayeredFS packaging in Python.
- Bundle keys, distribute game assets, or support an arbitrary remote tool download.
- Replace `nstool` or guarantee that a repository-bundled executable runs on every platform.

## Decisions

### Use a `uv` project with a standard console-script entry point

Create `pyproject.toml` with a `src/` package layout and a command such as `nsw-unpack`. Users can run it via `uv run nsw-unpack …` or install it from the project. This gives reproducible interpreter/dependency management without making the tool dependent on a global Python installation.

Alternative considered: retain Rust and invoke it from a Python script. This creates two packaging paths without improving the `nstool` wrapper, so the Python CLI replaces the placeholder rather than layering over it.

### Model extraction as two subcommands

Expose `nsw-unpack nsp INPUT --output DIR` and `nsw-unpack nca INPUT --keyset PATH --output DIR [--virtual-path PATH]`. Both accept `--nstool PATH` and `--overwrite`; NCA defaults the virtual path to `/`. The CLI translates these inputs to argument-list `subprocess` calls, never a shell command.

Alternative considered: a single command that infers format and switches behavior. Explicit subcommands yield clearer help, validation, and key requirements, and avoid ambiguous extension/content detection.

### Validate and protect paths before subprocess execution

Input files and keysets must be existing readable regular files. Outputs must be new, empty, or explicitly approved for overwrite; the CLI will create a missing output directory only after validation. It resolves the bundled executable relative to installed project/check-out resources and validates any user override as runnable. Error messages include the operation and safe command context; keys are never printed.

Alternative considered: delegate validation to `nstool`. Preflight checks prevent accidental writes and give consistent diagnostics before an external process starts.

### Isolate process execution behind an adapter

Put command construction and `subprocess.run` in a narrow `nstool` adapter that returns or raises structured outcomes. Command parsing, filesystem validation, NCA listing, and user-facing formatting remain separate. Tests mock the adapter/subprocess boundary to assert arguments, output protection, and propagated failures without needing real dumps or secret keysets.

Alternative considered: call `subprocess.run` directly in command handlers. This would make error mapping and tests repetitive and difficult to isolate.

## Risks / Trade-offs

- [A bundled `nstool` binary is absent or incompatible with the host] → Validate it early and document `--nstool` for a compatible local executable.
- [Keys or game paths contain sensitive information] → Do not log key values; use argument lists and redact keyset arguments from diagnostics where needed.
- [`nstool` extraction behavior varies for NCA layouts or updates] → Preserve its stderr, support explicit virtual paths, and limit this CLI to invoking documented `nstool` extraction behavior.
- [Overwrite can mix stale and new extraction files] → Default to rejection and require an explicit overwrite flag; document that users should prefer a clean destination.

## Migration Plan

1. Add the Python/uv package and documentation without deleting existing local binaries or game dumps.
2. Replace the placeholder execution path with the documented `uv run` command.
3. Validate the CLI using mocked tests and a user-owned sample only when available.
4. Roll back by removing the Python package files; no source game content is modified by the CLI, and extracted output remains user-controlled.

## Open Questions

None. The initial command names and options are intentionally specified in this design; additional game-specific extraction workflows can be added in later changes.

# Design

## Context

See `proposal.md` for background and motivation.
Currently, `src/nsw_localize/nstool.py` defines `resolve_nstool(override, repository_root)`. When `override` is not provided, it looks exclusively for `(repository_root or Path.cwd()) / "nstool"`.
Both `nstool` (POSIX executable) and `nstool.exe` (Windows executable) exist in the repository root. On Windows environments, resolving `./nstool` fails with `NstoolError` because `nstool` either does not exist or lacks Windows execution metadata, while `nstool.exe` is present and functional.

## Goals / Non-Goals

**Goals:**
- Automatically resolve `nstool.exe` when running on Windows (`sys.platform == "win32"`), falling back to `nstool` if `nstool.exe` is missing.
- Automatically resolve `nstool` when running on macOS, Linux, or other POSIX systems, falling back to `nstool.exe` if present.
- Preserve strict behavior when an explicit `--nstool` override path is passed: do not auto-append extensions or silently switch paths when user explicitly supplied an override.
- Ensure executable check (`os.access(..., os.X_OK)`) is handled safely across platforms.
- Update CLI help messages and error diagnostics to reflect the platform-specific default.

**Non-Goals:**
- Downloading or auto-compiling `nstool` binaries from GitHub releases.
- Modifying `nstool` command-line argument construction or output parsing logic.

## Decisions

### Decision 1: Platform detection and candidate binary order
- Use `sys.platform == "win32"` to determine whether the host OS is Windows.
- Define a candidate list of binary names based on platform:
  - If Windows: `["nstool.exe", "nstool"]`
  - If macOS / Linux / other: `["nstool", "nstool.exe"]`
- In `resolve_nstool(override=None, repository_root=None)`:
  - When `override` is given: check only `override.expanduser()`.
  - When `override` is omitted: search the candidate names in order within `(repository_root or Path.cwd())`. Select the first candidate file that exists.
- *Alternatives considered*:
  - Checking `PATH` via `shutil.which`: Skipped for default bundled discovery to keep deterministic repo-bundled behavior, but can be considered if repo-bundled binary is absent. The project design currently focuses on the bundled binaries at repository root.
  - Hardcoding solely `nstool.exe` on Windows without fallback: Fallback to `nstool` allows WSL or Cygwin/cross-environments to work seamlessly if only `nstool` exists.

### Decision 2: Cross-platform executable permission checks
- On POSIX (macOS/Linux), verify `candidate.is_file()` and `os.access(candidate, os.X_OK)`.
- On Windows (`sys.platform == "win32"`), `os.access(candidate, os.X_OK)` in Python checks for executable extensions (`.exe`, `.bat`, etc.) or returns true for any readable file depending on Windows version and filesystem. We will check `os.access(candidate, os.X_OK)` or `.exe` suffix to ensure consistent behavior across OSes without false permission denials.

### Decision 3: CLI parser help string
- Update `_add_common_options` in `src/nsw_localize/cli.py` to display dynamic or general help:
  `defaults to ./nstool.exe on Windows, ./nstool on macOS/Linux`.

## Risks / Trade-offs

- **[Risk] Path case sensitivity on Windows vs macOS** → Handled: `resolve_nstool` resolves paths with `.resolve()` and respects exact filenames `nstool.exe` and `nstool`.
- **[Risk] Existing unit tests mocking `Path.is_file` or `os.access`** → Handled: Tests will be updated or parameterized to verify both `win32` platform detection branch and POSIX branch using `unittest.mock.patch("sys.platform", ...)`.

# Proposal

## Why

Currently, `nsl` hardcodes discovery of the bundled NSTool executable to `./nstool` without considering the operating system platform. On Windows, the binary executable has the `.exe` extension (`nstool.exe`), causing `nsl` commands to fail looking for `nstool` instead of `nstool.exe`. Supporting cross-platform executable resolution enables developers and users on both Windows and macOS (or Linux) to run `nsl` unpack and merge workflows out of the box.

## What Changes

- Update default executable resolution in `nsw_localize.nstool.resolve_nstool` to detect OS platform:
  - On Windows (`sys.platform == "win32"`), default to looking for `nstool.exe` first, then fall back to `nstool`.
  - On macOS / Linux / POSIX systems, default to looking for `nstool` first, then fall back to `nstool.exe`.
- Update command-line help texts and documentation to reflect platform-appropriate defaults (`nstool.exe` on Windows, `nstool` on macOS/Linux).
- Ensure file permission checks (`os.X_OK`) behave gracefully across operating systems (especially Windows where `os.access(..., os.X_OK)` behaves differently or files rely on `.exe` extensions).

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `switch-content-unpacking`: Update the requirement for bundled executable discovery and protected execution diagnostics to specify platform-aware executable selection (`nstool.exe` on Windows and `nstool` on macOS/POSIX).

## Impact

- `src/nsw_localize/nstool.py`: `resolve_nstool` logic updated with platform awareness.
- `src/nsw_localize/cli.py`: default help text for `--nstool` clarifies platform default (`nstool.exe` on Windows, `nstool` on macOS/Linux).
- `tests/test_nstool.py` and `tests/test_cli.py`: updated and extended with cross-platform executable resolution test cases.
- Documentation / README if applicable.

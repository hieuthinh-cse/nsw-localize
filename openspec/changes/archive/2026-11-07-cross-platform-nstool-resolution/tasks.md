# Tasks

## 1. Cross-Platform Executable Resolution

- [x] 1.1 Implement platform-aware bundled binary candidate resolution in `src/nsw_localize/nstool.py` (preferring `nstool.exe` on Windows and `nstool` on POSIX/macOS) and verify that explicit overrides remain unaltered.
- [x] 1.2 Update executable permission validation in `src/nsw_localize/nstool.py` to handle Windows binary execution semantics cleanly without spurious permission failures.
- [x] 1.3 Add unit tests in `tests/test_nstool.py` mocking `sys.platform` to verify Windows resolution (`nstool.exe`), macOS/POSIX resolution (`nstool`), fallback resolution, and override preservation. Run tests with `uv run python -m unittest discover -s tests`.

## 2. CLI and Documentation Updates

- [x] 2.1 Update CLI argument help text for `--nstool` in `src/nsw_localize/cli.py` to describe platform defaults (`nstool.exe` on Windows, `nstool` on macOS/Linux) and verify `nsl --help` and `nsl unpack --help` display the updated description.
- [x] 2.2 Update unit tests in `tests/test_cli.py` to verify help text outputs and argument handling across platforms using `uv run python -m unittest discover -s tests`.
- [x] 2.3 Update `README.md` and `AGENTS.md` to document cross-platform executable usage and bundled binary details on Windows vs macOS.

## 3. Integration Verification

- [x] 3.1 Run the complete test suite via `uv run python -m unittest discover -s tests` to verify all tests pass without regressions.

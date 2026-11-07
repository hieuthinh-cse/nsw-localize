# Tasks: Add NCA Merge Command

## 1. Core NSTool helpers

- [x] 1.1 Implement `resolve_keyset` in `src/nsw_localize/nstool.py` with support for explicit overrides and fallback to `~/.switch/prod.keys`.
- [x] 1.2 Implement `build_nca_merge_args` in `src/nsw_localize/nstool.py` to target RomFS partition `/1` and supply `--basenca`.
- [x] 1.3 Add unit tests in `tests/test_nstool.py` covering `resolve_keyset` (override, default fallback, and missing file error) and `build_nca_merge_args`.

## 2. CLI integration

- [x] 2.1 Register the `merge-nca` subcommand in `src/nsw_localize/cli.py` with arguments `--base`, `--patch`, `--output`, `--keyset`, `--tik`, `--nstool`, and `--overwrite`.
- [x] 2.2 Implement the `_extract_merged_nca` command handler with input validation and execution dispatch.
- [x] 2.3 Add unit tests in `tests/test_cli.py` for `merge-nca` covering successful invocation, keyset default resolution, `--tik` passing, overwrite protection, and input validation failures.

## 3. Documentation

- [x] 3.1 Update `README.md` and `AGENTS.md` with usage instructions and examples for `nsw-unpack merge-nca`.
- [x] 3.2 Run test suite (`uv run pytest` / `python -m unittest`) and ruff checks to verify clean code quality.

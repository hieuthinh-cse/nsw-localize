# Tasks

## 1. UV project foundation

- [x] 1.1 Create the `pyproject.toml`, `src/` package layout, console-script entry point, and `uv` configuration; verify `uv run nsw-unpack --help` exits successfully.
- [x] 1.2 Replace or retire the Rust placeholder from the documented execution path and update `.gitignore` for Python caches and generated extraction output; verify `git status --ignored` identifies only the intended generated paths.

## 2. Safe NSTool integration

- [x] 2.1 Implement executable discovery and override validation, including clear missing/unrunnable-binary errors; verify unit tests cover bundled, explicit, and unavailable executable paths.
- [x] 2.2 Implement input/keyset and output-directory validation with explicit overwrite protection; verify unit tests confirm invalid paths and non-empty destinations do not invoke the process runner.
- [x] 2.3 Implement the argument-list `nstool` process adapter with NSP/NCA command builders, stderr propagation, and redacted diagnostics; verify mocked-subprocess tests assert the command arguments and nonzero failure handling.

## 3. Extraction commands

- [x] 3.1 Implement the `nsp` subcommand to extract an NSP and list resulting NCA paths; verify command-level tests cover a successful extraction and invalid NSP input.
- [x] 3.2 Implement the `nca` subcommand with required keyset, output, optional virtual path, `--nstool`, and `--overwrite` options; verify command-level tests cover root extraction, selected virtual-path extraction, and preflight rejection.
- [x] 3.3 Add consistent exit codes and concise user-facing success/error messages for both subcommands; verify end-to-end mocked CLI tests cover success, process failure, and missing executable outcomes.

## 4. Documentation and validation

- [x] 4.1 Document prerequisites, legal key/game ownership boundary, `uv` setup, NSP and NCA examples, `--nstool`, virtual paths, and overwrite behavior in the README; verify every documented command is accepted by CLI help or tests.
- [x] 4.2 Run the complete test suite and formatting/lint checks configured by the project; verify the commands pass from a clean checkout without real game content or keys.

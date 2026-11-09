# Tasks

## 1. Confirm NSTool key-input contract

- [x] 1.1 Run a read-only NSTool spike against representative base/update tickets and document whether a combined keyset, `--tik`, or direct `--titlekey` arguments are required; verify the result with a clean temporary environment and redact all key values.
- [x] 1.2 Define the CLI option names and compatibility behavior from the spike; verify `nsl merge-nca --help` describes base/update ticket and title-key inputs without exposing secrets.

## 2. Implement title-key preparation

- [x] 2.1 Add title-key extraction and validation helpers for base and update tickets, including Rights ID matching, malformed-input errors, and duplicate-conflict detection; verify with unit tests using synthetic non-secret fixtures.
- [x] 2.2 Add secure temporary keyset creation and cleanup for one merge invocation; verify cleanup on success and subprocess failure without modifying `~/.switch/title.keys`.
- [x] 2.3 Add secret-safe diagnostics and tests proving title-key values never appear in command errors, captured logs, or test output.

## 3. Integrate merge-nca

- [x] 3.1 Extend merge argument parsing and validation to accept the base/update ticket and title-key inputs defined by the NSTool spike; verify invalid and missing inputs fail before extraction.
- [x] 3.2 Update the NSTool command adapter to invoke the selected key-input strategy for both base and update Rights IDs; verify mocked subprocess arguments include the base NCA, update NCA, `/1`, and required key material without logging values.
- [x] 3.3 Preserve the existing global-key compatibility path while making explicit prepared key material deterministic; verify existing merge CLI tests still pass and new tests cover a clean environment without global `title.keys`.

## 4. Documentation and integration verification

- [x] 4.1 Update README and the relevant merge skill instructions with the two-ticket/title-key workflow, safe temporary-key behavior, and failure diagnostics; verify every documented command matches CLI help.
- [x] 4.2 Run the full test suite and a representative base/update merge using clean temporary key locations; verify the output contains the expected RomFS files and no title-key values are printed.

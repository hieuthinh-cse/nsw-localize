# Proposal

## Why

The repository has locally owned Nintendo Switch game dumps and an `nstool` binary, but no repeatable command interface for extracting their NSP and NCA contents. A Python CLI managed with `uv` will make the first stage of the localization workflow explicit, safer, and easier to reproduce.

## What Changes

- Add a Python command-line application, packaged and run with `uv`, for unpacking an NSP and individual NCAs through the repository's `nstool` executable.
- Provide an NSP workflow that extracts the PFS0 contents, identifies the extracted NCA files, and reports the files available for follow-up extraction.
- Provide an NCA workflow that invokes `nstool` with a user-supplied keyset and extracts the requested NCA contents to a chosen output directory.
- Validate input paths and output destinations before invoking `nstool`, surface the wrapped command's failure clearly, and avoid silently overwriting an existing extraction.
- Add automated tests that mock the external executable, plus usage documentation and `.gitignore` coverage for generated extraction directories.

## Capabilities

### New Capabilities

- `switch-content-unpacking`: Extract NSP package contents and NCA filesystem contents through a validated Python CLI wrapper around `nstool`.

### Modified Capabilities

None.

## Impact

- Adds Python project metadata, a `uv`-managed CLI entry point, application code, tests, and user documentation.
- Uses the existing repository-local `nstool` binary at runtime; users must provide legally dumped compatible keysets and game content.
- Supersedes the current placeholder `src/main.rs` as the project's executable implementation; Rust packaging is not part of the new CLI path.

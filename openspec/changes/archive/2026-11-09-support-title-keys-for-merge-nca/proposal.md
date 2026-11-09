# Proposal

## Why

`merge-nca` currently accepts `prod.keys` and an optional ticket, but successful base/update decryption also depends on title-key entries. In practice, the workflow silently relies on `~/.switch/title.keys`, so a valid explicit keyset and ticket can still produce an empty or failed merge.

## What Changes

- Make title-key handling an explicit part of the base-plus-update merge workflow.
- Support extracting or preparing title-key entries for both the base and update tickets before invoking `nstool`.
- Allow merge execution to use the prepared title-key material without relying on an implicit global `~/.switch/title.keys` file.
- Preserve key confidentiality: never print title-key values or commit generated key files.
- Add validation, diagnostics, and tests for missing, malformed, and duplicate base/update title-key entries.

## Capabilities

### New Capabilities

- `nca-title-key-preparation`: Prepare title-key material for base and update NCAs from their tickets for a merge operation.

### Modified Capabilities

- `switch-content-unpacking`: Change `merge-nca` so its documented decryption inputs include the title keys required by both base and update NCAs, with deterministic behavior when they are supplied explicitly.

## Impact

- CLI argument handling and merge orchestration in `src/nsw_localize/cli.py` and `src/nsw_localize/nstool.py`.
- New unit tests for key preparation, command construction, validation, and secret-safe diagnostics.
- README and project skill documentation for the revised merge workflow.
- No change to the underlying `nstool` binary or to committed game/key assets.

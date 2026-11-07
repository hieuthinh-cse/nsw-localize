# Proposal: Add NCA Merge Command

## Why

Nintendo Switch game updates provide delta patches for the game's RomFS using the BKTR format inside update Program NCAs. In order to inspect, extract, or localize games with updates applied, users need a way to combine the base Program NCA with the update Program NCA.

Currently, the `nsw-unpack` CLI only provides basic `nsp` and `nca` extraction without exposing base NCA combining or keyset defaulting. Users are forced to manually invoke external tools or write ad-hoc scripts, which contradicts the project's rule that all Switch extraction operations must be routed through `nsw-unpack`.

## What Changes

- Add a dedicated `merge-nca` subcommand to `nsw-unpack`.
- Require `--base` (base Program NCA) and `--patch` (update Program NCA).
- Target RomFS partition extraction (`/1`) automatically through `nstool --basenca <base_nca>`, eliminating the need for users to manually configure virtual paths.
- Support default keyset resolution from `~/.switch/prod.keys` when `--keyset` is not explicitly provided.
- Support optional `--tik` parameter for encrypted eShop update packages.
- Validate input paths (base NCA, patch NCA, keyset, ticket) and enforce overwrite protection before executing `nstool`.
- Add comprehensive automated unit tests covering argument construction, CLI parsing, validation error handling, and subprocess execution.

## Capabilities

### Modified Capabilities

- `switch-content-unpacking`: Add merged RomFS extraction from base and update NCAs.

## Impact

- Extends `src/nsw_localize/nstool.py` and `src/nsw_localize/cli.py`.
- Keeps existing `nsp` and `nca` commands backward-compatible.
- Updates tests in `tests/test_nstool.py` and `tests/test_cli.py`.
- Extends user documentation in `README.md` and `AGENTS.md`.

# Spec Delta: Switch Content Unpacking - NCA Merge

## Purpose

Extend the Nintendo Switch content unpacking CLI to support extracting merged RomFS filesystems from base and update NCAs using `nstool`.

## ADDED Requirements

### Requirement: Merged NCA content extraction
The CLI SHALL provide a `merge-nca` command that accepts a base Program NCA path, an update Program NCA path, a keyset path (with fallback to `~/.switch/prod.keys`), an output directory, and an optional ticket path, extracting the merged RomFS partition (`/1`) via `nstool`.

#### Scenario: Extract merged RomFS from base and update NCAs
- **WHEN** a user runs `nsw-unpack merge-nca` with valid base NCA, update NCA, keyset, and an empty output directory
- **THEN** the CLI invokes `nstool` with `--basenca <base_nca>`, the keyset, virtual path `/1`, and the update NCA, extracting the merged RomFS into the output directory.

#### Scenario: Default keyset discovery
- **WHEN** a user omits `--keyset` and `~/.switch/prod.keys` exists and is readable
- **THEN** the CLI automatically uses `~/.switch/prod.keys` as the keyset.

#### Scenario: Keyset missing and not provided
- **WHEN** a user omits `--keyset` and `~/.switch/prod.keys` does not exist or is not readable
- **THEN** the CLI exits nonzero before invoking `nstool` and instructs the user to provide `--keyset` or configure `~/.switch/prod.keys`.

#### Scenario: Reject missing or unreadable base or patch NCA
- **WHEN** either the base NCA or patch NCA path is missing, not a regular file, or not readable
- **THEN** the CLI exits nonzero before invoking `nstool` and identifies the invalid path.

#### Scenario: Support optional ticket file
- **WHEN** a user supplies `--tik <tik_path>`
- **THEN** the CLI validates the ticket path exists and is readable, and passes `--tik <tik_path>` to `nstool`.

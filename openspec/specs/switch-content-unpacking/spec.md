# Switch Content Unpacking Specification

## Purpose

Provide a safe, repeatable command-line workflow for extracting legally owned Nintendo Switch package and archive content with `nstool`.

## Requirements

### Requirement: NSP package extraction
The CLI SHALL provide an NSP extraction command under `nsl unpack nsp` that accepts an NSP input path and output directory, extracts the package contents through `nstool`, and reports the extracted NCA files for subsequent use.

#### Scenario: Extract a valid NSP
- **WHEN** a user runs `nsl unpack nsp` with an existing NSP and a new or empty output directory
- **THEN** the CLI invokes `nstool` to extract the package and prints the paths of extracted NCA files

#### Scenario: Reject a missing or unsupported package input
- **WHEN** a user supplies a missing file or a file not identified as an NSP to `nsl unpack nsp`
- **THEN** the CLI exits nonzero without invoking `nstool` and explains the invalid input

### Requirement: NCA content extraction
The CLI SHALL provide an NCA extraction command under `nsl unpack nca` that accepts an NCA input path, a readable keyset path, an output directory, an optional NCA virtual path to extract, defaulting to the archive root, and an optional ticket path to pass to NSTool.

#### Scenario: Extract NCA contents with a keyset
- **WHEN** a user runs `nsl unpack nca` with an existing NCA, readable keyset, and new or empty output directory
- **THEN** the CLI invokes `nstool` with the keyset and requested virtual path and reports the output location on success

#### Scenario: Extract NCA contents with a ticket
- **WHEN** a user runs `nsl unpack nca` with an existing NCA, readable keyset, readable `.tik` file, and new or empty output directory
- **THEN** the CLI passes both the keyset and ticket to `nstool` before extracting the requested content

#### Scenario: Extract one NCA partition
- **WHEN** a user supplies a valid NCA virtual path such as a partition path to `nsl unpack nca`
- **THEN** the CLI passes that path to `nstool` and extracts only the selected content into the output directory

#### Scenario: Reject unavailable decryption material
- **WHEN** the NCA input or keyset path does not exist or is not readable when running `nsl unpack nca`
- **THEN** the CLI exits nonzero before extraction and identifies the unavailable path

#### Scenario: Reject an unavailable ticket
- **WHEN** a user supplies a missing, unreadable, or non-ticket path to `--tik`
- **THEN** the CLI exits nonzero before extraction and identifies the invalid ticket input

### Requirement: Protected execution and diagnostics
The CLI SHALL require explicit overwrite consent before writing into a non-empty output directory, locate the platform-appropriate bundled NSTool executable (`nstool.exe` on Windows, `nstool` on macOS/POSIX) or accept an explicit executable path, and return actionable diagnostics for executable or extraction failures.

#### Scenario: Refuse a non-empty destination by default
- **WHEN** a user selects an output directory that already contains files without an overwrite option
- **THEN** the CLI exits nonzero without invoking `nstool` and preserves the destination contents

#### Scenario: Accept an explicit overwrite request
- **WHEN** a user selects a non-empty output directory with the overwrite option
- **THEN** the CLI permits `nstool` to write the requested extraction there

#### Scenario: Discover bundled executable on Windows
- **WHEN** the CLI resolves the bundled executable on a Windows host without an explicit `--nstool` override
- **THEN** the CLI searches for `nstool.exe` before falling back to `nstool` in the bundled search directory

#### Scenario: Discover bundled executable on macOS and POSIX systems
- **WHEN** the CLI resolves the bundled executable on macOS or POSIX systems without an explicit `--nstool` override
- **THEN** the CLI searches for `nstool` before falling back to `nstool.exe` in the bundled search directory

#### Scenario: Report a missing executable
- **WHEN** neither the bundled nor explicitly configured `nstool` executable is runnable
- **THEN** the CLI exits nonzero and explains how to supply a valid executable path

#### Scenario: Preserve an external-tool failure
- **WHEN** `nstool` terminates unsuccessfully
- **THEN** the CLI exits nonzero and shows the attempted operation together with the tool's diagnostic output

### Requirement: UV-installable command interface
The project SHALL expose the CLI as the `nsl` executable and document execution through `uv run nsl`, supporting `nsl unpack nsp`, `nsl unpack nca`, and top-level `nsl merge-nca`.

#### Scenario: Run from a UV-managed checkout
- **WHEN** a user follows the documented `uv run nsl` command from a checkout with supported Python available
- **THEN** the CLI starts and displays the available commands (`unpack`, `merge-nca`)

### Requirement: Merged NCA content extraction
The CLI SHALL provide a top-level `merge-nca` command (`nsl merge-nca`) that accepts a base Program NCA path, an update Program NCA path, a keyset path (with fallback to `~/.switch/prod.keys`), an output directory, optional base and update ticket paths, and the title-key material required by both NCAs, extracting the merged RomFS partition (`/1`) via `nstool`.

#### Scenario: Extract merged RomFS from base and update NCAs
- **WHEN** a user runs `nsl merge-nca` with valid base and update NCAs, a usable keyset, both required title keys, and an empty output directory
- **THEN** the CLI invokes `nstool` with the base NCA, update NCA, title-key material, virtual path `/1`, and extracts the merged RomFS into the output directory

#### Scenario: Prepare title keys from supplied tickets
- **WHEN** a user supplies readable base and update tickets without pre-existing title-key entries
- **THEN** the CLI prepares both entries before invoking the merge and does not require a global `~/.switch/title.keys` file

#### Scenario: Reject incomplete title-key material
- **WHEN** the merge cannot obtain a title key for either the base or update Rights ID
- **THEN** the CLI exits nonzero before extraction and identifies which decryption input is unavailable without printing key values

#### Scenario: Default keyset discovery
- **WHEN** a user omits `--keyset` and `~/.switch/prod.keys` exists and is readable
- **THEN** the CLI automatically uses `~/.switch/prod.keys` as the keyset while resolving title-key material according to the merge inputs

#### Scenario: Keyset missing and not provided
- **WHEN** a user omits `--keyset` and `~/.switch/prod.keys` does not exist or is not readable
- **THEN** the CLI exits nonzero before invoking `nstool` and instructs the user to provide `--keyset` or configure `~/.switch/prod.keys`

#### Scenario: Reject missing or unreadable base or patch NCA
- **WHEN** either the base NCA or patch NCA path is missing, not a regular file, or not readable
- **THEN** the CLI exits nonzero before invoking `nstool` and identifies the invalid path

#### Scenario: Support ticket files for both inputs
- **WHEN** a user supplies base and update ticket paths to `nsl merge-nca`
- **THEN** the CLI validates both paths and uses them to prepare the title keys required for the merge

#### Scenario: Support optional ticket file
- **WHEN** a user supplies the supported ticket option to `nsl merge-nca`
- **THEN** the CLI validates the ticket path and passes the ticket input to the title-key preparation and merge operation

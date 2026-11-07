# Spec Delta

## Purpose

Provide a safe, repeatable command-line workflow for extracting legally owned Nintendo Switch package and archive content with `nstool`.

## ADDED Requirements

### Requirement: NSP package extraction
The CLI SHALL provide an NSP extraction command that accepts an NSP input path and output directory, extracts the package contents through `nstool`, and reports the extracted NCA files for subsequent use.

#### Scenario: Extract a valid NSP
- **WHEN** a user runs the NSP extraction command with an existing NSP and a new or empty output directory
- **THEN** the CLI invokes `nstool` to extract the package and prints the paths of extracted NCA files

#### Scenario: Reject a missing or unsupported package input
- **WHEN** a user supplies a missing file or a file not identified as an NSP to the NSP extraction command
- **THEN** the CLI exits nonzero without invoking `nstool` and explains the invalid input

### Requirement: NCA content extraction
The CLI SHALL provide an NCA extraction command that accepts an NCA input path, a readable keyset path, an output directory, and an optional NCA virtual path to extract, defaulting to the archive root.

#### Scenario: Extract NCA contents with a keyset
- **WHEN** a user runs the NCA extraction command with an existing NCA, readable keyset, and new or empty output directory
- **THEN** the CLI invokes `nstool` with the keyset and requested virtual path and reports the output location on success

#### Scenario: Extract one NCA partition
- **WHEN** a user supplies a valid NCA virtual path such as a partition path
- **THEN** the CLI passes that path to `nstool` and extracts only the selected content into the output directory

#### Scenario: Reject unavailable decryption material
- **WHEN** the NCA input or keyset path does not exist or is not readable
- **THEN** the CLI exits nonzero before extraction and identifies the unavailable path

### Requirement: Protected execution and diagnostics
The CLI SHALL require explicit overwrite consent before writing into a non-empty output directory, locate the bundled `nstool` executable or accept an explicit executable path, and return actionable diagnostics for executable or extraction failures.

#### Scenario: Refuse a non-empty destination by default
- **WHEN** a user selects an output directory that already contains files without an overwrite option
- **THEN** the CLI exits nonzero without invoking `nstool` and preserves the destination contents

#### Scenario: Accept an explicit overwrite request
- **WHEN** a user selects a non-empty output directory with the overwrite option
- **THEN** the CLI permits `nstool` to write the requested extraction there

#### Scenario: Report a missing executable
- **WHEN** neither the bundled nor explicitly configured `nstool` executable is runnable
- **THEN** the CLI exits nonzero and explains how to supply a valid executable path

#### Scenario: Preserve an external-tool failure
- **WHEN** `nstool` terminates unsuccessfully
- **THEN** the CLI exits nonzero and shows the attempted operation together with the tool's diagnostic output

### Requirement: UV-installable command interface
The project SHALL expose the unpacking CLI as an installable Python command and document execution through `uv`, including the NSP and NCA command forms and required keyset input.

#### Scenario: Run from a UV-managed checkout
- **WHEN** a user follows the documented `uv` command from a checkout with supported Python available
- **THEN** the unpacking CLI starts and displays its subcommand help or runs the requested extraction

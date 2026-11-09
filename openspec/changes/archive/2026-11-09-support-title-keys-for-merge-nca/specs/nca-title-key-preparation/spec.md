# Spec Delta

## Purpose

Provide a repeatable, secret-safe way to prepare title-key entries required to decrypt matching base and update Nintendo Switch NCAs during localization workflows.

## ADDED Requirements

### Requirement: Prepare title keys for both merge inputs
The workflow SHALL be able to prepare title-key entries for the base and update tickets used by one merge operation.

#### Scenario: Both tickets provide title-key data
- **WHEN** a merge workflow receives readable base and update ticket files
- **THEN** it produces entries keyed by each ticket's Rights ID for use by the merge invocation

#### Scenario: One required ticket is unavailable
- **WHEN** either the base or update ticket cannot be read or does not contain usable title-key data
- **THEN** preparation fails before extraction and identifies the missing input without exposing key material

### Requirement: Write a valid keyset representation
Prepared entries SHALL be written in the accepted keyset format with one complete entry per line and no accidental concatenation between entries.

#### Scenario: Entries are written to a project-local keyset
- **WHEN** preparation targets a project-local title-key file
- **THEN** each base and update entry is separated by a newline and the output path is reported without printing values

#### Scenario: Existing matching entry is present
- **WHEN** the target keyset already contains an entry for a Rights ID
- **THEN** preparation does not create a duplicate conflicting entry

### Requirement: Protect title-key values
The workflow SHALL keep title-key values out of normal command output, diagnostics, tests, and committed project artifacts.

#### Scenario: Preparation succeeds
- **WHEN** title keys are extracted and written
- **THEN** user-facing output reports only safe metadata such as Rights IDs and file paths

#### Scenario: External tool reports a key-related error
- **WHEN** the underlying tool fails while processing key material
- **THEN** the workflow preserves an actionable non-secret diagnostic and omits key values

# Spec Delta

## MODIFIED Requirements

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

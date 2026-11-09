# Spec Delta

## MODIFIED Requirements

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

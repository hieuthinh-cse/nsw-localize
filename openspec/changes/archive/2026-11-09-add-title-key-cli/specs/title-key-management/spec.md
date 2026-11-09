# Spec Delta

## Purpose

Provide a safe, repeatable command for maintaining persistent Nintendo Switch title-key entries from ticket files across supported operating systems.

## ADDED Requirements

### Requirement: Add a title-key entry from a ticket
The CLI SHALL provide `nsl add-title-key --tik <ticket>` to read one usable title-key entry from a Nintendo Switch ticket and persist it in a title-key file.

#### Scenario: Add entry to the default key file
- **WHEN** the user runs the command with a readable valid ticket and no output override
- **THEN** the CLI writes the ticket's Rights ID and title key as one valid entry in the user's `.switch/title.keys` file and reports the destination without printing the title-key value

#### Scenario: Add entry to an explicit key file
- **WHEN** the user supplies an explicit output path and a readable valid ticket
- **THEN** the CLI writes the entry to that path and preserves unrelated existing entries

### Requirement: Resolve and create the default Switch key location
The CLI SHALL resolve the default title-key path relative to the current user's home directory and create missing parent directories or files as needed.

#### Scenario: Resolve the default path on POSIX
- **WHEN** the command runs on macOS or Linux without an output override
- **THEN** it targets `<home>/.switch/title.keys`

#### Scenario: Resolve the default path on Windows
- **WHEN** the command runs on Windows without an output override
- **THEN** it targets `%USERPROFILE%\\.switch\\title.keys` using platform-native path handling

### Requirement: Handle duplicate and conflicting entries safely
The CLI SHALL avoid duplicate matching entries and SHALL reject a different key for an existing Rights ID unless explicit overwrite behavior is requested.

#### Scenario: Matching entry already exists
- **WHEN** the target key file contains the same Rights ID with the same title key
- **THEN** the command succeeds without adding a duplicate line

#### Scenario: Conflicting entry exists
- **WHEN** the target key file contains the same Rights ID with a different title key and overwrite is not requested
- **THEN** the command fails without changing the target file and does not expose either key value

#### Scenario: Explicit overwrite is requested
- **WHEN** the target key file contains the same Rights ID with a different title key and the user supplies the supported force option
- **THEN** the command replaces that entry while preserving unrelated entries and reports only safe metadata

### Requirement: Protect title-key material
The workflow SHALL keep title-key values out of normal output, diagnostics, tests, and generated project artifacts.

#### Scenario: Ticket or key file is invalid
- **WHEN** the ticket or target key file cannot be read or parsed
- **THEN** the command returns a non-secret actionable error without printing title-key-sized values

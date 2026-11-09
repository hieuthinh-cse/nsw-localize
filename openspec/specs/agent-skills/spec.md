# Agent Skills Specification

## Purpose

Define standardized agent skill workflows and boundaries for extracting and merging Nintendo Switch game content using the project CLI.

## Requirements

### Requirement: Switch package unpack skill (ns-unpack)
The repository SHALL provide an agent skill named `ns-unpack` located at `.agents/skills/ns-unpack/SKILL.md` that instructs agents to unpack NSP packages and extract NCA partitions exclusively via `uv run nsl unpack`.

#### Scenario: Agent unpacks NSP package
- **WHEN** an agent is directed to unpack an NSP package using `ns-unpack`
- **THEN** the skill guides the agent to execute `uv run nsl unpack nsp` with the NSP path and output destination

#### Scenario: Agent unpacks NCA partition
- **WHEN** an agent is directed to extract RomFS (`/1`) or ExeFS (`/0`) from an unpacked NCA
- **THEN** the skill guides the agent to execute `uv run nsl unpack nca` with the appropriate virtual path and keyset

#### Scenario: Guidance for update packages
- **WHEN** an agent encounters a BKTR update NCA requiring patch merging
- **THEN** the skill directs the agent to utilize the `ns-merge-nca` skill rather than attempting a standalone unpack

### Requirement: Merged content extraction skill (ns-merge-nca)
The repository SHALL provide an agent skill named `ns-merge-nca` located at `.agents/skills/ns-merge-nca/SKILL.md` that instructs agents to merge base and update packages into a unified RomFS exclusively via `uv run nsl merge-nca`.

#### Scenario: Agent merges base and update content
- **WHEN** an agent is directed to merge a base game and update patch
- **THEN** the skill instructs the agent to unpack both packages with `ns-unpack` if in NSP format and execute `uv run nsl merge-nca` with the base Program NCA, patch Program NCA, and any ticket file

#### Scenario: Locating game.win in merged RomFS
- **WHEN** the target game is a GameMaker title and merged RomFS extraction completes
- **THEN** the skill instructs the agent to inspect and copy `game.win` from the merged RomFS and verify its SHA-256 digest

### Requirement: Elimination of legacy skill binaries and scripts
The repository SHALL NOT retain standalone `hactool.exe` binaries or legacy extraction scripts within agent skill directories.

#### Scenario: Skill directory contents
- **WHEN** the agent skill directories `.agents/skills/ns-unpack` and `.agents/skills/ns-merge-nca` are inspected
- **THEN** neither directory contains bundled Windows executable binaries or legacy Python helper scripts

### Requirement: Title-key preparation skill
The repository SHALL provide an agent skill named `ns-add-title-key` at `.agents/skills/ns-add-title-key/SKILL.md` that guides agents to prepare persistent title-key entries exclusively through `uv run nsl add-title-key`.

#### Scenario: Agent prepares a title key
- **WHEN** an agent is directed to add a Nintendo Switch title key from a ticket
- **THEN** the skill instructs the agent to run `uv run nsl add-title-key --tik <ticket>` and verify the safe result path without invoking NSTool directly

#### Scenario: Agent works across operating systems
- **WHEN** the workflow runs on Windows, macOS, or Linux
- **THEN** the skill uses platform-neutral paths and explains that the CLI resolves the default `.switch/title.keys` location from the user's home directory

#### Scenario: Agent handles sensitive key material
- **WHEN** the skill workflow reports success or failure
- **THEN** it instructs the agent not to print, commit, or place ticket/title-key values in logs or project artifacts

# Spec Delta

## Purpose

Provide authorized Discord users a safe, repeatable way to initialize
localization project workspaces and their workflow manifests.

## ADDED Requirements

### Requirement: Authorized project-creation command
The system SHALL expose a `/create` Discord application command that accepts a project name and permits it only for a server administrator or a member holding at least one configured creation role.

#### Scenario: Member with an allowed role creates a project
- **WHEN** a guild member with a configured creation role invokes `/create` with a valid project name
- **THEN** the system creates the project workspace and confirms it to that member

#### Scenario: Server administrator creates a project
- **WHEN** a guild member with the Discord Administrator permission invokes `/create` with a valid project name
- **THEN** the system creates the project workspace even when the member has no configured creation role

#### Scenario: Unauthorized member invokes the command
- **WHEN** a guild member without the Administrator permission or a configured creation role invokes `/create`
- **THEN** the system does not create or modify a workspace and returns a private authorization-denied response

#### Scenario: Command is used outside a guild
- **WHEN** `/create` is invoked where guild roles and permissions are unavailable
- **THEN** the system does not create or modify a workspace and returns a private response that the command requires a server

### Requirement: Safe project name resolution
The system SHALL resolve each valid project name to a normalized directory name beneath the configured projects root and SHALL reject names that are empty after normalization or would resolve outside that root.

#### Scenario: Project name is normalized
- **WHEN** an authorized member submits a valid project name containing spaces or mixed case
- **THEN** the system uses its normalized directory name consistently for workspace creation and duplicate detection

#### Scenario: Invalid project name is rejected
- **WHEN** an authorized member submits a name that is empty after normalization or contains a path traversal attempt
- **THEN** the system does not create or modify a workspace and returns a private validation error

### Requirement: Initialized workflow workspace
The system SHALL create a new project directory containing `workflow.yaml`, `rom/base/`, `rom/update/`, and `output/`, with the manifest recording the supplied project name, integer version `1`, base and update inputs, and output path.

#### Scenario: Workspace creation succeeds
- **WHEN** an authorized member creates a project whose normalized directory does not exist
- **THEN** the system creates all required directories and a manifest equivalent to:
  ```yaml
  name: <supplied project name>
  version: 1

  game:
    input:
      - base: ./rom/base/
      - update: ./rom/update/
    output: ./output/
  ```

#### Scenario: Existing normalized directory is preserved
- **WHEN** an authorized member creates a project whose normalized directory already exists
- **THEN** the system makes no changes to that directory and returns a private response that the project already exists

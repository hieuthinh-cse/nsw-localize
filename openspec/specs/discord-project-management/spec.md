# Discord Project Management Specification

## Purpose

Provide authorized Discord users a safe, repeatable way to initialize
localization project workspaces and their workflow manifests.

## Requirements

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
The system SHALL create a new project directory containing `workflow.yaml`, `rom/base/`, `rom/update/`, and `output/`, with the manifest recording the supplied project name, integer version `1`, base and update inputs, output path, and the Discord forum post ID created for that project.

#### Scenario: Workspace creation succeeds
- **WHEN** an authorized member creates a project whose normalized directory does not exist and its forum post is created
- **THEN** the system creates all required directories and a manifest equivalent to:
  ```yaml
  name: <supplied project name>
  version: 1
  forum_post_id: <Discord post ID>

  game:
    input:
      - base: ./rom/base/
      - update: ./rom/update/
    output: ./output/
  ```

#### Scenario: Existing normalized directory is preserved
- **WHEN** an authorized member creates a project whose normalized directory already exists
- **THEN** the system makes no changes to that directory and returns a private response that the project already exists

### Requirement: Forum channel configuration
The system SHALL require a positive Discord forum-channel ID configuration for project creation and SHALL reject missing, malformed, or non-forum configured channels before creating a workspace.

#### Scenario: Valid forum channel is configured
- **WHEN** the bot starts with a valid configured forum-channel ID
- **THEN** authorized project-creation requests can use that forum as their project-discussion destination

#### Scenario: Forum channel configuration is invalid
- **WHEN** the forum-channel ID is absent, malformed, or resolves to a channel that is not a forum
- **THEN** the system does not create a workspace and returns an actionable configuration error

### Requirement: Project forum post provisioning
The system SHALL create one discussion post in the configured forum for each successfully created project, using the project identity in the post title, and SHALL persist the resulting post ID in that project's workflow manifest.

#### Scenario: Forum post and workspace are created
- **WHEN** an authorized member creates a project and the configured forum accepts the post
- **THEN** the system creates the workspace, records the post ID in `workflow.yaml`, and privately confirms the project and forum post to the member

#### Scenario: Forum post creation fails
- **WHEN** an authorized member creates a project but the configured forum cannot create its post
- **THEN** the system returns a private actionable error and leaves no newly created project workspace behind

### Requirement: Environment file configuration loading
The system SHALL load environment variables from a local `.env` file upon configuration loading without overriding existing process environment variables.

#### Scenario: Existing environment variables take precedence
- **WHEN** a variable exists in both the process environment and a `.env` file
- **THEN** the system preserves the value from the process environment

#### Scenario: Missing environment variables fallback to .env
- **WHEN** required configuration variables are not set in the process environment but exist in a `.env` file
- **THEN** the system loads and uses the values defined in the `.env` file

#### Scenario: Missing .env file is handled gracefully
- **WHEN** no `.env` file exists and all required variables are set in the environment
- **THEN** the system loads the configuration normally without raising an error

### Requirement: Forum post mention acknowledgment
The system SHALL reply to bot mentions occurring within discussion posts in the configured forum channel when the message author is an administrator or holds an authorized creation role, and SHALL ignore all other mentions.

#### Scenario: Authorized member mentions bot in forum post
- **WHEN** an authorized member tags the bot inside a thread belonging to the configured forum channel
- **THEN** the system replies to that message with "hi" and mentions the author

#### Scenario: Server administrator mentions bot in forum post
- **WHEN** a member with the Administrator permission tags the bot inside a thread belonging to the configured forum channel
- **THEN** the system replies to that message with "hi" and mentions the author

#### Scenario: Unauthorized member mentions bot in forum post
- **WHEN** a member without the Administrator permission or an authorized role tags the bot inside a forum post
- **THEN** the system produces no response and remains silent

#### Scenario: Bot is mentioned outside configured forum channel
- **WHEN** an authorized member tags the bot in a channel or thread that does not belong to the configured forum channel
- **THEN** the system produces no response and remains silent

#### Scenario: Bot message mentions itself
- **WHEN** a bot or webhook posts a message mentioning the bot
- **THEN** the system ignores the message and produces no response

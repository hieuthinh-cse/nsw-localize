# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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

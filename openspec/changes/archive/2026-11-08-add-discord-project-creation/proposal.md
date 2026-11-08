# Proposal

## Why

Localization projects need a consistent, safely created workspace before the
game packages are extracted. A Discord slash command lets authorized team
members initialize that workspace without manually creating folders or a
workflow manifest.

## What Changes

- Add a Discord bot with a `/create` application command that creates a new
  project workspace beneath the repository's `projects/` directory.
- Create `workflow.yaml` plus the `rom/base`, `rom/update`, and `output`
  directories for each new project.
- Normalize and validate the supplied project name before using it as a
  directory name, preventing paths outside the projects root.
- Refuse duplicate project names without modifying the existing workspace.
- Restrict project creation to members with a configured allowed Discord role,
  while allowing Discord server administrators to bypass that role check.

## Capabilities

### New Capabilities

- `discord-project-management`: Create initialized localization project
  workspaces through an authorized Discord slash command.

### Modified Capabilities

- None.

## Impact

- Affected code: a new bot entry point and project-workspace creation service,
  with tests for authorization, name handling, and filesystem behavior.
- Dependencies: a Discord Python client library and YAML serialization support.
- Configuration: Discord bot token and allowed role IDs supplied through
  environment variables; `projects/` becomes the managed workspace root.

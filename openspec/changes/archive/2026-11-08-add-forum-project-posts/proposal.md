# Proposal

## Why

Creating a localization workspace through Discord does not create the associated discussion thread, so contributors have no canonical forum post for coordination. Capturing the forum post identifier in the workspace manifest will link the local project to its Discord discussion.

## What Changes

- Add a required Discord forum-channel configuration setting, sourced from the existing sample environment configuration.
- When an authorized `/create` request successfully initializes a project, create a forum post for that project and record its Discord post/thread ID in `workflow.yaml`.
- Report forum-post creation failures without leaving an unlinked, successful-looking project workspace.
- Document the required bot permission and forum-channel configuration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `discord-project-management`: Project creation now provisions a Discord forum post and persists its identifier in the workflow manifest.

## Impact

- Affected code: bot configuration, `/create` command handling, workspace manifest creation, and their tests.
- Affected operations: Discord bot environment configuration and permissions; `DISCORD_LOCALIZE_NSW_CHANNEL_ID` in `.env.example` identifies the target forum channel.
- No new third-party dependency is expected; the existing `discord.py` client creates the forum thread.

# Design

## Context

The existing bot authorizes `/create`, then synchronously creates a directory tree and `workflow.yaml`. `BotConfig` currently contains only the token, creation-role IDs, and project root. The sample environment already supplies `DISCORD_LOCALIZE_NSW_CHANNEL_ID`, but the application neither parses it nor uses it. See `proposal.md` for motivation and the specification delta for required behavior.

## Goals / Non-Goals

**Goals:**

- Make a forum post and its manifest reference part of one successful project-provisioning operation.
- Validate configuration and the resolved Discord channel before filesystem mutation.
- Preserve existing authorization and duplicate-directory safety semantics.
- Give the requester an actionable private failure response.

**Non-Goals:**

- Migrating existing project manifests or retrospectively creating posts for them.
- Creating a dedicated Discord channel, assigning post tags, or synchronizing later edits between Discord and `workflow.yaml`.
- Changing who is authorized to invoke `/create`.

## Decisions

### Treat `DISCORD_LOCALIZE_NSW_CHANNEL_ID` as a required positive integer setting

Extend `BotConfig` and environment validation with a `forum_channel_id` field sourced from the setting already shown in `.env.example`; document it along with the permission needed to create forum threads. Reject an omitted, non-numeric, or non-positive value at startup.

Using the existing sample name avoids introducing a duplicate configuration surface. The category setting in the sample is out of scope because a forum post is created in the forum channel itself, not in its parent category.

### Validate the target forum before workspace creation

After authorization and project-name/path validation, obtain the configured channel from the guild/cache and, if necessary, fetch it. Confirm that it is a Discord forum channel before creating any local files. Use the submitted display name for the post title, subject to Discord's title rules.

This fails early for stale, inaccessible, or incorrectly typed channel IDs. Deferring the interaction response before network work prevents Discord's response deadline from making an otherwise successful request appear to fail. A generic text-channel API was considered but rejected because it cannot create a forum post.

### Create the forum post first and compensate on local failure

Create the forum thread/post, then pass its numeric ID into workspace/manifest creation. Extend manifest generation and workspace creation to require that ID and write `forum_post_id` at the top level. If local creation fails after the post succeeds, attempt to delete the just-created post; always report the workspace failure privately. If post creation fails, never call workspace creation.

This ordering directly guarantees no new local workspace is left when Discord posting fails and keeps the manifest complete at its first write. Creating the workspace first was rejected because it requires rollback after every Discord failure and risks an incomplete manifest. Distributed atomicity is unavailable; the compensating deletion reduces, but cannot eliminate, orphan-post risk if Discord deletion also fails.

### Keep the existing explicit error taxonomy and add Discord failures

Configuration, invalid/absent forum channel, forum creation, and filesystem errors receive distinct private messages. The success response identifies the workspace and links or identifies the created post. Tests mock Discord calls and assert both filesystem state and the manifest post ID.

## Risks / Trade-offs

- [Bot lacks permission or the configured ID is stale] → Validate channel type/access and surface a configuration-focused error; document required permissions.
- [Filesystem failure after a successful post] → Attempt best-effort post deletion and report any cleanup limitation in logs/error details without claiming success.
- [Interaction response expires during Discord I/O] → Defer the ephemeral response before network operations and use a follow-up response.
- [Forum title constraints reject a supplied name] → Convert the Discord exception to a private actionable failure and create no workspace.

## Migration Plan

1. Deploy the configuration and bot changes with `DISCORD_LOCALIZE_NSW_CHANNEL_ID` set to the intended forum channel and permission to create public threads/posts.
2. Verify a new `/create` request produces a forum post and a manifest containing its ID.
3. Roll back by restoring the prior bot version; already-created project manifests and forum posts remain valid records and require no destructive migration.

# Tasks

## 1. Configuration and manifest contract

- [x] 1.1 Extend bot configuration to parse and validate `DISCORD_LOCALIZE_NSW_CHANNEL_ID` as a required positive forum-channel ID, and add configuration unit tests for valid, missing, malformed, and non-positive values.
- [x] 1.2 Extend workspace manifest generation and project creation to require and persist `forum_post_id`, and update project-workspace tests to verify the complete manifest and rollback behavior.
- [x] 1.3 Update `.env.example` and the Discord bot README setup/permissions documentation for the forum setting, and verify every documented setting matches configuration loading.

## 2. Forum-backed project creation

- [x] 2.1 Resolve and validate the configured guild channel as a Discord forum before filesystem mutation, with handler tests covering absent, inaccessible, and wrong-type channels.
- [x] 2.2 Update `/create` to defer its private response, create one forum post with the project name, pass the post ID into workspace creation, and verify the success response plus manifest ID in integration-style handler tests.
- [x] 2.3 Handle forum-post API failures without calling workspace creation, and verify a private actionable error and no new project directory.
- [x] 2.4 Compensate for workspace creation failure after a successful forum post by deleting the newly created post best-effort, and verify the cleanup attempt and error response with mocked Discord and filesystem failures.

## 3. Regression verification

- [x] 3.1 Run `uv run python -m unittest discover -s tests -v` and verify existing authorization, duplicate-directory, and invalid-name behavior remains covered and passing.

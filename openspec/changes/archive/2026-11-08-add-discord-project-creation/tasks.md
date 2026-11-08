# Tasks

## 1. Bot runtime and configuration

- [x] 1.1 Add the Discord client and YAML serialization dependencies plus a dedicated bot entry point, and verify the package installs and the bot entry point displays its configuration error when required variables are absent.
- [x] 1.2 Implement startup configuration parsing for `DISCORD_TOKEN` and comma-separated `DISCORD_CREATE_ROLE_IDS`, and verify unit tests cover valid values, missing values, malformed role IDs, and duplicate IDs.
- [x] 1.3 Document bot setup, required Discord permissions, environment variables, and the command invocation, and verify the documented startup command runs to its expected configuration check.

## 2. Authorization and project workspace services

- [x] 2.1 Implement the pure authorization policy granting access to Discord administrators and members with an allowed role, and verify unit tests cover both allowed paths and denied members.
- [x] 2.2 Implement validated ASCII-slug project-name resolution rooted under `projects/`, and verify unit tests reject empty, traversal, separator, and root-escape inputs while covering normalization.
- [x] 2.3 Implement non-overwriting workspace initialization with `workflow.yaml`, `rom/base`, `rom/update`, and `output`, and verify filesystem tests assert the exact parsed manifest and directory layout.
- [x] 2.4 Handle existing normalized project directories and recoverable creation failures without changing pre-existing content, and verify tests assert duplicate preservation and cleanup is limited to request-created paths.

## 3. Discord command integration

- [x] 3.1 Register `/create` as a guild-aware Discord application command that delegates authorization and initialization to the services, and verify interaction-handler tests cover an allowed role and an administrator.
- [x] 3.2 Return private, actionable command responses for unauthorized members, direct-message use, invalid names, duplicate projects, and initialization failures, and verify each outcome with mocked interactions.
- [x] 3.3 Synchronize the command according to the documented deployment flow and verify an integration smoke test can construct the bot and register the command without connecting to Discord.

## 4. Regression verification

- [x] 4.1 Run the complete unit-test suite, including the existing `nsl` CLI tests and new bot/service tests, and verify all tests pass.
- [x] 4.2 Run Ruff against the updated source and tests, and verify it reports no lint errors.

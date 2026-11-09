# Proposal

## Why

The project can currently derive title-key entries from tickets for an individual merge invocation, but it has no safe, repeatable command for adding a ticket's entry to the user's persistent Switch keyset. This makes eShop NCA workflows unnecessarily manual and leaves the documented `~/.switch/title.keys` preparation step outside the project CLI.

## What Changes

- Add `nsl add-title-key --tik <ticket>` to extract one title-key entry from a ticket and persist it in the user's `.switch/title.keys` file.
- Resolve the default destination cross-platform using the current user's home directory (`~/.switch/title.keys` on POSIX and `%USERPROFILE%\\.switch\\title.keys` on Windows).
- Create the `.switch` directory and key file when they do not exist, while preserving unrelated existing entries.
- Detect and safely handle duplicate matching entries and conflicting entries for the same Rights ID; never print title-key values.
- Add tests and documentation for the command, including Windows path behavior.
- Add the repository skill `.agents/skills/ns-add-title-key/SKILL.md` to guide agents through this workflow using `uv run nsl`.

## Capabilities

### New Capabilities

- `title-key-management`: Persist and safely maintain title-key entries derived from Nintendo Switch ticket files.

### Modified Capabilities

- `agent-skills`: Add the `ns-add-title-key` skill alongside the existing Switch extraction and merge skills.

## Impact

- Affected CLI parser and title-key helper module under `src/nsw_localize/`.
- New command-level and title-key persistence tests.
- README and agent-skill documentation.
- No new runtime dependencies and no direct invocation of NSTool.

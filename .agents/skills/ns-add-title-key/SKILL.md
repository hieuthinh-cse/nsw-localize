---
name: ns-add-title-key
description: Add a Nintendo Switch title-key entry from a ticket to the user's persistent .switch/title.keys using the nsl CLI.
---

# Add a Switch Title Key

Use this skill when a localization workflow needs to persist a title-key entry extracted from a Nintendo Switch ticket.

## Workflow

Run the project CLI through `uv`:

```sh
uv run nsl add-title-key --tik "path/to/game.tik"
```

The command writes to the user's default key file:

- Windows: `%USERPROFILE%\\.switch\\title.keys`
- macOS/Linux: `~/.switch/title.keys`

For an explicit destination:

```sh
uv run nsl add-title-key \
  --tik "path/to/game.tik" \
  --output "path/to/title.keys"
```

If the same Rights ID already exists with a different key, the command stops safely. Use `--force` only when the replacement is intentional.

The input is a ticket; an NCA is not required. The CLI creates the `.switch` directory when needed, avoids duplicate matching entries, and preserves unrelated keyset lines.

## Security Constraints

- Use only tickets and game content the user owns or is authorized to inspect.
- Never print or paste title-key values into chat, logs, commits, or project files.
- Report only safe metadata such as the Rights ID and destination path.
- Use `uv run nsl`; do not invoke external extraction binaries directly for this workflow.

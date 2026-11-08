# Design

## Context

See `proposal.md` for motivation. Currently, `load_bot_config()` in `src/nsw_localize/config.py` inspects `os.environ` directly without loading local `.env` files. In `src/nsw_localize/bot.py`, `LocalizationBot` only registers the `/create` slash command and does not listen to message events.

## Goals / Non-Goals

**Goals:**
- Load environment variables from `.env` using `python-dotenv` prior to resolving config, giving precedence to existing process environment variables.
- Listen for message events in `LocalizationBot` and detect mentions targeting the bot.
- Acknowledge mentions inside forum post threads belonging to `config.forum_channel_id` if the sender has Administrator rights or an authorized role, replying with "hi" and mentioning the author.
- Silently ignore mentions from unauthorized members, other bots, or outside the configured forum channel.

**Non-Goals:**
- Validating or parsing complex text commands within mention content (e.g. natural language processing).
- Verifying workspace directories or `workflow.yaml` manifest existence when handling mentions.
- Dynamic hot-reloading of `.env` files while the bot process is actively running.

## Decisions

### 1. Use `python-dotenv` with `override=False`
- **Choice**: Add `python-dotenv>=1.0.0` to project dependencies and invoke `load_dotenv(override=False)` inside `load_bot_config()` when reading default environment variables.
- **Rationale**: `python-dotenv` standardizes parsing of quotes, multiline values, and comments without rolling a custom fragile parser. `override=False` ensures that environment variables explicitly exported in CI/CD or containers take precedence.
- **Alternatives considered**:
  - *Standard library parser*: Avoids adding a dependency but requires custom handling of edge cases (quoted strings, export statements, comments).
  - *Calling `load_dotenv` only in `main()`*: Leaves helper scripts or tests that invoke `load_bot_config()` without `.env` support unless explicitly called.

### 2. Handle mentions via `on_message` event in `LocalizationBot`
- **Choice**: Implement `on_message` on `LocalizationBot` with the following verification pipeline:
  1. Guard against bot messages: `if message.author.bot or message.author == self.user: return`
  2. Guard against missing mentions: `if self.user not in message.mentions: return`
  3. Validate channel context: Verify `isinstance(message.channel, discord.Thread)` and `message.channel.parent_id == self.config.forum_channel_id`.
  4. Validate sender permissions: Inspect `message.author.guild_permissions.administrator` and `[r.id for r in message.author.roles]`, passing them to `is_authorized_to_create_project(..., allowed_role_ids=self.config.create_role_ids)`.
  5. Reply: If authorized, call `await message.reply("hi", mention_author=True)`. If unauthorized, return silently.
- **Rationale**: Keeps authorization rules consistent with the `/create` command and leverages Discord's native inline reply mechanism.
- **Alternatives considered**:
  - *Replying with plain channel send (`channel.send(f"{author.mention} hi")`)*: Lacks visual message context linking back to the user's mention.
  - *Replying with error message for unauthorized users*: Creates noisy chat logs and risks spam attacks from unprivileged users pinging the bot.

### 3. Gateway Intents configuration
- **Choice**: Enable `intents.message_content = True` in `LocalizationBot` initialization so mention detection and message processing operate reliably across Discord server settings.
- **Rationale**: While Discord delivers basic mention metadata for direct bot pings, `message_content` intent ensures message and channel structures are reliably populated.

## Risks / Trade-offs

- **[Risk] Test pollution when `.env` exists in the working directory during tests** → Mitigation: In `tests/test_config.py`, pass isolated `env={...}` mappings or monkeypatch `dotenv.load_dotenv` to avoid accidental dependencies on developer local `.env` files.
- **[Risk] Permissions check on webhook or non-member authors** → Mitigation: Verify `isinstance(message.author, discord.Member)` before reading `guild_permissions` and `roles`. If author is not a Member (e.g. DM or webhook), silently ignore.

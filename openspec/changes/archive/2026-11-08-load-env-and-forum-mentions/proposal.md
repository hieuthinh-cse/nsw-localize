# Proposal

## Why

The Discord bot currently requires configuration variables to be exported directly into the shell environment before launch, making local operations and deployment workflows prone to missing variable errors. Additionally, team members discussing localization projects in Discord forum posts have no direct way to test bot responsiveness or ping the bot for status acknowledgment.

## What Changes

- Add automatic `.env` file loading via `python-dotenv` prior to reading configuration variables, while maintaining shell environment precedence.
- Add an event handler for forum post messages where the bot is mentioned/tagged.
- Acknowledge authorized mentions in forum post threads by replying "hi" with user tagging enabled.
- Silently ignore mentions from unauthorized members or outside configured forum post threads.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `discord-project-management`: Add requirements for automatic `.env` file configuration loading and authorized forum post mention responses.

## Impact

- **Dependencies**: Adds `python-dotenv>=1.0.0` to `pyproject.toml`.
- **Code**:
  - `src/nsw_localize/config.py`: Load `.env` into environment before reading variables.
  - `src/nsw_localize/bot.py`: Handle `on_message` to detect bot mentions within forum channel threads and verify authorization against administrator status and `DISCORD_CREATE_ROLE_IDS`.
- **Testing**: Add unit tests for `.env` fallback loading in `tests/test_config.py` and mention handling tests in `tests/test_bot.py`.

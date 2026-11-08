# Tasks

## 1. Environment Loading Dependency and Configuration

- [x] 1.1 Add `python-dotenv>=1.0.0` to dependencies in `pyproject.toml` and verify package installation using `uv sync`
- [x] 1.2 Update `src/nsw_localize/config.py` to invoke `dotenv.load_dotenv(override=False)` when resolving default environment variables and verify configuration loading
- [x] 1.3 Add unit tests in `tests/test_config.py` verifying `.env` fallback loading, missing file tolerance, and environment variable precedence

## 2. Forum Post Mention Event Handling

- [x] 2.1 Update `LocalizationBot` in `src/nsw_localize/bot.py` to enable `message_content` intent and add `on_message` handler that verifies forum channel thread location, checks administrator / role permissions, and replies "hi" with user tagging
- [x] 2.2 Add tests in `tests/test_bot.py` verifying reply behavior for authorized member mentions, silence for unauthorized mentions, silence for bot messages, and silence outside the configured forum channel

## 3. Verification and Documentation

- [x] 3.1 Run test suite and linter via `pytest` and `ruff check` to verify all tests pass with zero lint errors
- [x] 3.2 Update `.env.example` and `README.md` to document `.env` file loading behavior and forum post mention interactions

# Spec Delta

## ADDED Requirements

### Requirement: Environment file configuration loading
The system SHALL load environment variables from a local `.env` file upon configuration loading without overriding existing process environment variables.

#### Scenario: Existing environment variables take precedence
- **WHEN** a variable exists in both the process environment and a `.env` file
- **THEN** the system preserves the value from the process environment

#### Scenario: Missing environment variables fallback to .env
- **WHEN** required configuration variables are not set in the process environment but exist in a `.env` file
- **THEN** the system loads and uses the values defined in the `.env` file

#### Scenario: Missing .env file is handled gracefully
- **WHEN** no `.env` file exists and all required variables are set in the environment
- **THEN** the system loads the configuration normally without raising an error

### Requirement: Forum post mention acknowledgment
The system SHALL reply to bot mentions occurring within discussion posts in the configured forum channel when the message author is an administrator or holds an authorized creation role, and SHALL ignore all other mentions.

#### Scenario: Authorized member mentions bot in forum post
- **WHEN** an authorized member tags the bot inside a thread belonging to the configured forum channel
- **THEN** the system replies to that message with "hi" and mentions the author

#### Scenario: Server administrator mentions bot in forum post
- **WHEN** a member with the Administrator permission tags the bot inside a thread belonging to the configured forum channel
- **THEN** the system replies to that message with "hi" and mentions the author

#### Scenario: Unauthorized member mentions bot in forum post
- **WHEN** a member without the Administrator permission or an authorized role tags the bot inside a forum post
- **THEN** the system produces no response and remains silent

#### Scenario: Bot is mentioned outside configured forum channel
- **WHEN** an authorized member tags the bot in a channel or thread that does not belong to the configured forum channel
- **THEN** the system produces no response and remains silent

#### Scenario: Bot message mentions itself
- **WHEN** a bot or webhook posts a message mentioning the bot
- **THEN** the system ignores the message and produces no response

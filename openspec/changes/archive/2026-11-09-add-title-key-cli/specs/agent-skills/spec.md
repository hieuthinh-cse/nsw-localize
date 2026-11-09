# Spec Delta

## ADDED Requirements

### Requirement: Title-key preparation skill
The repository SHALL provide an agent skill named `ns-add-title-key` at `.agents/skills/ns-add-title-key/SKILL.md` that guides agents to prepare persistent title-key entries exclusively through `uv run nsl add-title-key`.

#### Scenario: Agent prepares a title key
- **WHEN** an agent is directed to add a Nintendo Switch title key from a ticket
- **THEN** the skill instructs the agent to run `uv run nsl add-title-key --tik <ticket>` and verify the safe result path without invoking NSTool directly

#### Scenario: Agent works across operating systems
- **WHEN** the workflow runs on Windows, macOS, or Linux
- **THEN** the skill uses platform-neutral paths and explains that the CLI resolves the default `.switch/title.keys` location from the user's home directory

#### Scenario: Agent handles sensitive key material
- **WHEN** the skill workflow reports success or failure
- **THEN** it instructs the agent not to print, commit, or place ticket/title-key values in logs or project artifacts

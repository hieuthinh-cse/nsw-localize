# Design

## Context

The repository currently provides a dependency-free Python 3.9 command-line
tool for Switch content extraction. It has no bot runtime, YAML handling, or
managed project workspace. See proposal.md for motivation and the delta spec
for the observable contract.

## Goals / Non-Goals

**Goals:**

- Add a small, independently testable Discord bot entry point.
- Keep authorization and filesystem decisions in pure services so they can be
  tested without Discord network access.
- Create a deterministic, non-overwriting workspace rooted at the repository's
  `projects/` directory.
- Keep secrets and Discord-specific deployment settings outside versioned
  project manifests.

**Non-Goals:**

- Extracting NSP/NCA content, running localization workflows, or uploading
  game files through Discord.
- Managing projects after creation, deleting workspaces, or changing existing
  `nsl` CLI commands.
- Implementing multi-server project isolation or a database.

## Decisions

### Discord application commands through a Python Discord client

Use `discord.py` and its native application-command support for `/create`.
It provides guild member roles and Administrator permission information needed
for the authorization decision. A handwritten Discord gateway/API client is
rejected because it would add protocol and command-registration maintenance.

### Environment-based bot configuration

Read the bot token from `DISCORD_TOKEN` and the comma-separated allowed role
IDs from `DISCORD_CREATE_ROLE_IDS`. Parse IDs at startup and fail clearly for
missing or malformed required configuration. Environment variables keep
credentials and deployment-specific role IDs out of source control; a
committed configuration file is rejected because it risks leaking the token
and makes per-server deployment less clear.

### Separate authorization and workspace services

Keep Discord interaction handling thin: it obtains the guild member and
delegates permission evaluation and workspace initialization to project-local
services. The authorization service grants access for Administrator or an
intersection of member role IDs and configured role IDs. The workspace service
accepts a projects root and a submitted name, returns a typed success or
failure result, and never depends on Discord objects. This isolates the
security-sensitive filesystem behavior for unit testing.

### Canonical filesystem-safe project slug

Normalize the submitted name to a lowercase ASCII slug: retain alphanumeric
words, join them with single hyphens, and reject a result that is empty. Reject
path separators, dot path components, and any resolution escaping the projects
root rather than attempting to reinterpret them. Store the trimmed submitted
name in the manifest while using the slug as the directory identifier. This
preserves a human-readable project name without allowing it to control paths.

### Atomic non-overwrite creation

Attempt creation of the project root as a new directory and treat an existing
directory as a conflict before creating the manifest or child directories.
Write the manifest only after the new root exists, then create the required
children. On a creation failure after the root is made, remove only files and
directories created during that request when safe to do so; never alter an
existing project. This minimizes partial workspaces while keeping the explicit
no-overwrite guarantee.

### Explicit YAML serialization

Use a YAML serializer to emit the fixed manifest structure with quoted values
when necessary, rather than assembling YAML text. This avoids malformed YAML
when a display name contains punctuation and keeps `version` an integer.

## Risks / Trade-offs

- [Discord role changes or bot permissions are unavailable at invocation] ->
  Evaluate the roles supplied by Discord for that interaction and deny on
  missing guild context; document the permissions and intents the bot needs.
- [Slug normalization makes distinct display names collide] -> Treat a slug
  collision as an existing project and report it without altering either one.
- [Process interruption leaves a partial new workspace] -> Use isolated root
  creation and best-effort cleanup limited to paths created by the request;
  surface an actionable failure to the caller.
- [A deployment runs from an unexpected working directory] -> Derive the
  default projects root from the package/repository configuration and allow a
  clearly documented test/deployment override rather than using the process
  current directory implicitly.

## Migration Plan

1. Add dependencies, configuration documentation, and the bot command without
   changing the existing `nsl` entry point.
2. Deploy with `DISCORD_TOKEN` and at least one `DISCORD_CREATE_ROLE_IDS`
   value, and grant the bot application-command and guild-member access.
3. Register/synchronize the command in the target guild and validate it with
   an allowed role, an administrator, and a denied member.
4. Roll back by stopping the bot process and removing its deployment
   configuration; existing created project workspaces remain untouched.

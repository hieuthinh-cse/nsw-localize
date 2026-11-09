# Proposal

## Why

`nsl unpack nca` can currently pass only a keyset to NSTool, even though the
underlying argument builder already supports a ticket. This prevents direct
extraction of encrypted standalone NCAs when the title key is available from
the matching `.tik` file, and leaves the CLI and agent skill documentation
out of sync.

## What Changes

- Add an optional `--tik` argument to `nsl unpack nca`.
- Validate the ticket path and pass it to NSTool during NCA extraction.
- Preserve the existing explicit `--keyset` behavior; do not introduce an
  ephemeral keyset flow.
- Add command-level tests for ticket forwarding and invalid ticket inputs.
- Update `README.md`, `AGENTS.md`, and `.agents/skills/ns-unpack/SKILL.md` with
  the supported `--tik` invocation and ticket-handling guidance.

## Capabilities

### New Capabilities

### Modified Capabilities

- `switch-content-unpacking`: NCA extraction accepts an optional ticket and
  forwards it to NSTool while retaining the existing keyset and validation
  requirements.

## Impact

- CLI parser and NCA extraction handler in `src/nsw_localize/cli.py`.
- Existing NSTool argument construction in `src/nsw_localize/nstool.py` is
  reused without changing its public argument shape.
- Unit tests in `tests/test_cli.py`.
- User and agent-facing documentation only; no new dependencies or key
  storage behavior.

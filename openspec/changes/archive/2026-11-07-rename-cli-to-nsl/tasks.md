# Tasks

## 1. Entry Points and Packaging

- [x] 1.1 Replace `nsw-unpack` with `nsl = "nsw_localize.cli:main"` in `pyproject.toml`, and verify with `uv sync` or test execution.

## 2. CLI Command Hierarchy

- [x] 2.1 Refactor `src/nsw_localize/cli.py` to structure commands with root `prog="nsl"`, adding `merge-nca` directly at root level and `nsp`, `nca` under an `unpack` subparser (`nsl unpack nsp`, `nsl unpack nca`, `nsl merge-nca`).

## 3. Test Suite Updates

- [x] 3.1 Update unit tests in `tests/test_cli.py` to test `nsl unpack nsp`, `nsl unpack nca`, and `nsl merge-nca`, verifying command parsing, exit codes, and output expectations.
- [x] 3.2 Verify test coverage and ensure old command paths (`nsp`, `nca` without `unpack`, or `nsw-unpack`) are removed from tests.

## 4. Documentation and Guidelines

- [x] 4.1 Update `README.md` and `AGENTS.md` to document `uv run nsl unpack nsp`, `uv run nsl unpack nca`, and `uv run nsl merge-nca`.
- [x] 4.2 Review and update any skill references in `.agents/skills/` to use `nsl unpack` and `nsl merge-nca`.

## Workflow follow-up

- Archive the change after implementation and test verification are complete.
- Verify the archived spec synchronization with `switch-content-unpacking`.

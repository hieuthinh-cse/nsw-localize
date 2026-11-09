# Tasks

## 1. Title-key file persistence

- [x] 1.1 Add a parser/serializer for persistent `Rights ID = title key` entries that preserves unrelated keyset lines and verify it with synthetic fixtures covering empty, existing, duplicate, malformed, and conflicting entries.
- [x] 1.2 Add default-path resolution and atomic persistence under `Path.home() / ".switch" / "title.keys"`, including parent creation, and verify POSIX and simulated Windows home paths without modifying the real user keyset.
- [x] 1.3 Implement duplicate no-op, conflict rejection, and explicit `--force` replacement behavior with secret-safe errors, and verify the original file remains unchanged after failed writes.

## 2. CLI command

- [x] 2.1 Register `nsl add-title-key --tik <ticket> [--output <path>] [--force]` and connect it to ticket extraction and persistence; verify parser help and successful command-level execution with mocked filesystem paths.
- [x] 2.2 Add CLI tests for invalid tickets, missing/unreadable targets, duplicate entries, conflicts, force replacement, output-path reporting, and absence of title-key values from stdout/stderr; verify the full CLI test suite passes.

## 3. Agent workflow and documentation

- [x] 3.1 Create `.agents/skills/ns-add-title-key/SKILL.md` with `uv run nsl` usage, ticket-only input, default `.switch/title.keys` behavior, Windows/macOS/Linux path guidance, and secret-handling constraints; verify it contains no direct NSTool invocation.
- [x] 3.2 Update README and relevant project guidance with the new command and safe usage examples; verify every documented invocation matches `nsl add-title-key --help`.

## 4. Integration verification

- [x] 4.1 Run the complete test suite, lint/format checks used by the repository, and OpenSpec validation; verify all pass without modifying or exposing any real key files.

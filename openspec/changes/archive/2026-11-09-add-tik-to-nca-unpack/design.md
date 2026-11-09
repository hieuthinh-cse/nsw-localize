# Design

## Context

`build_nca_extract_args()` already accepts an optional ticket path and emits
NSTool's `--tik` argument. The `unpack nca` parser and handler are the missing
integration point; they currently require only `--keyset`. The existing
`merge-nca` ticket behavior is not reused because this change intentionally
does not create an ephemeral keyset.

## Goals / Non-Goals

**Goals:**

- Expose the existing NSTool ticket argument through `unpack nca`.
- Validate the supplied ticket before creating the output directory or invoking
  NSTool.
- Keep keyset handling, virtual-path handling, diagnostics, and overwrite
  semantics unchanged.
- Make the CLI, README, AGENTS instructions, and `ns-unpack` skill agree.

**Non-Goals:**

- No ephemeral keyset creation or title-key extraction.
- No changes to `merge-nca` behavior.
- No automatic discovery of ticket files.

## Decisions

- Add `--tik` as an optional `Path` argument to `unpack nca`, matching the
  existing `merge-nca` naming and NSTool option.
- Keep `--keyset` required for `unpack nca`; a ticket supplies title-key
  material but does not replace the base keyset needed by NSTool.
- Validate `--tik` with the existing readable-file validator and `.tik`
  suffix check, then pass the resolved path to `build_nca_extract_args()`.
- Add one success test that asserts `--tik` and its resolved path are sent to
  the mocked NSTool runner, plus validation coverage for an invalid ticket.

## Risks / Trade-offs

- [Users may assume a ticket alone is sufficient] -> Keep `--keyset` required
  and document both arguments in the skill and README.
- [Ticket contents may contain secret material] -> Log only paths and retain
  existing redaction behavior; never print ticket bytes or title-key values.

## Migration Plan

No migration is required. Existing commands remain valid; users who have a
matching ticket may add `--tik <ticket>` to `unpack nca`.

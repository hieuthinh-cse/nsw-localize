# Design

## Context

The CLI currently resolves one `prod.keys` file and passes it to `nstool`, while `nstool` may separately depend on title-key entries discovered in `~/.switch/title.keys`. A base/update merge therefore has an implicit global dependency and can fail even when the caller supplies a ticket. See proposal.md and the spec deltas for the required behavior.

## Goals / Non-Goals

**Goals:**

- Make title-key preparation for both Rights IDs explicit and deterministic.
- Support project-local or temporary key material without mutating the user's global key files.
- Keep key values out of logs, exceptions, test fixtures, and committed artifacts.
- Preserve the existing `nsl merge-nca` flow and NSTool-based extraction behavior.

**Non-Goals:**

- Implementing cryptography or replacing `nstool`'s decryption engine.
- Dumping keys from a console or bypassing ownership checks.
- Changing ordinary NSP extraction or unrelated NCA partition extraction.

## Decisions

### Use both tickets as merge inputs

The merge path will identify the base and update Rights IDs and prepare both title-key entries. The update ticket remains the required ticket for the patched Program NCA, while the base ticket supplies the matching base entry. This avoids assuming that one title key can decrypt both archives.

### Keep preparation separate from extraction

Key preparation will be a small adapter/helper with validation and secret-safe output. The existing command builder will consume the resulting keyset or direct key arguments, keeping subprocess invocation and filesystem validation testable independently.

### Prefer ephemeral key material for automatic preparation

When keys are derived from supplied tickets, the implementation should use a temporary keyset for the invocation and remove it after the process completes. An explicit project-local keyset may be supported for repeatable workflows, but the CLI must never modify `~/.switch/title.keys` implicitly.

### Add explicit ticket inputs while preserving compatibility

The merge interface should accept separate base and update ticket paths, while retaining the existing update-ticket behavior as a compatibility path only when the base title key is already available. The help and README must make the two-ticket path the recommended form.

### Redact secrets at every boundary

Command construction and error reporting must avoid rendering title-key values. Tests will assert argument shape and metadata handling without embedding real key material.

## Risks / Trade-offs

- [NSTool may only discover title keys through a particular keyset format or global location] -> Add an adapter that builds the format NSTool accepts, test command construction, and report a clear unsupported-format error.
- [Temporary files may remain after interruption] -> Use secure temporary directories, cleanup in `finally`, and avoid writing them under the repository by default.
- [Existing users may provide only `--tik`] -> Preserve the old argument as a compatibility mode and emit a diagnostic that a base ticket or explicit base title key is required when the base key is unavailable.
- [Duplicate Rights IDs may have conflicting values] -> Reject conflicting duplicates rather than silently choosing one.

## Migration Plan

1. Add the new preparation and merge-input options without removing existing flags.
2. Update tests and documentation to show base and update ticket usage.
3. Verify merges using a clean temporary key environment with no global `title.keys` dependency.
4. Keep the old global discovery path as a documented compatibility fallback until a later breaking change is approved.

## Open Questions

- The bundled NSTool v1.9.2 help confirms `--tik` and `--titlekey` for NCA input and `--basenca` for update extraction. Because direct `--titlekey` accepts one value, the implementation uses a disposable combined keyset for the two-ticket merge path. No representative real tickets are committed or available in the repository; synthetic fixtures validate offsets and formatting without containing secrets.

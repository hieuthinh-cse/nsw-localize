# Design

## Context

See proposal.md for motivation. The existing `titlekeys.py` already parses ticket metadata into `TitleKeyEntry` values and has secret-safe validation helpers, while `nsl merge-nca` currently uses temporary keysets for deterministic merge operations. The new command needs persistent-file behavior without changing that ephemeral merge path.

## Goals / Non-Goals

**Goals:**

- Reuse the existing ticket parser and validation model.
- Maintain a human-readable `RightsID = TITLEKEY` keyset format with stable, newline-separated entries.
- Resolve the default destination with `Path.home()` so Windows and POSIX platforms behave consistently.
- Update files safely, preserving unrelated entries and avoiding partial writes.
- Keep diagnostics secret-safe and expose a small CLI surface with an explicit `--force` override.

**Non-Goals:**

- Deriving a title key from an NCA; the title key comes from the ticket.
- Invoking NSTool or decrypting an NCA.
- Automatically discovering tickets or modifying `prod.keys`.
- Adding a bundled binary or a runtime dependency.

## Decisions

1. **Use the ticket as the only required input.** The NCA is not needed to obtain the title-key bytes, so `--nca` is intentionally out of scope. This keeps the command honest about its source of key material and usable with a ticket alone.

2. **Default to `Path.home() / ".switch" / "title.keys"`.** This maps to the established Switch key location on Windows (`%USERPROFILE%\\.switch\\title.keys`) and POSIX systems without shell-specific expansion.

3. **Parse and rewrite the key file through structured entries.** Read existing non-empty key lines, normalize the supported `Rights ID = title key` representation, merge by Rights ID, and write a complete file with one entry per line. Preserve unrelated valid lines if the file contains other keyset material; reject malformed or ambiguous title-key lines rather than silently corrupting them.

4. **Make conflict handling explicit.** An identical existing entry is a no-op. A conflicting Rights ID fails by default; `--force` replaces only that entry. Use an atomic temporary file in the destination directory followed by replacement to reduce the risk of truncating the user's key file.

5. **Keep secret-safe reporting centralized.** Success output may include the Rights ID and destination path, while errors identify the ticket/path or conflict without title-key values. Tests use synthetic fixtures and assert that secret values do not appear in captured output.

6. **Add a focused repository skill.** `ns-add-title-key` documents the CLI workflow, home-directory resolution, Windows compatibility, and secret-handling constraints. It must direct agents through `uv run nsl`, never direct NSTool invocation.

## Risks / Trade-offs

- [Risk] Existing `title.keys` files may contain formatting variants or comments. -> Mitigation: define the accepted parser behavior in tests, preserve unrelated lines where possible, and fail safely on ambiguous title-key entries.
- [Risk] A filesystem replacement can fail on permissions or concurrent edits. -> Mitigation: write in the destination directory, surface a non-secret error, and avoid deleting or truncating the original before replacement succeeds.
- [Risk] `--force` can replace a legitimate entry. -> Mitigation: require the explicit flag and report only the Rights ID and destination.

## Migration Plan

No migration is required. Existing users can continue using `title.keys`; the new command is additive. If a command invocation fails, the original key file remains unchanged.

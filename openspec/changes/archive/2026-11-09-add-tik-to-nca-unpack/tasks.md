# Tasks

## 1. Extend NCA CLI ticket handling

- [x] 1.1 Add optional `--tik` to `unpack nca`, validate it as a readable `.tik` file, and pass the resolved path to the existing NCA argument builder; verify with CLI tests that NSTool receives `--tik` and the ticket path.
- [x] 1.2 Add failure coverage for a missing or invalid `--tik` input and verify NSTool is not invoked.

## 2. Synchronize user and agent documentation

- [x] 2.1 Update `README.md` with a direct `unpack nca --keyset ... --tik ...` example and clarify that no ephemeral keyset is created; verify the documented command matches `nsl unpack nca --help`.
- [x] 2.2 Update `AGENTS.md` and `.agents/skills/ns-unpack/SKILL.md` to map ticket files to `--tik` for standalone NCA extraction while retaining `merge-nca` guidance for BKTR updates; verify both documents contain the supported argument names.

## 3. Run integration verification

- [x] 3.1 Run the full test suite and OpenSpec validation; verify all tests pass and `openspec validate --change add-tik-to-nca-unpack --strict` succeeds.

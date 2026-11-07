# Spec Delta

## MODIFIED Requirements

### Requirement: Protected execution and diagnostics
The CLI SHALL require explicit overwrite consent before writing into a non-empty output directory, locate the platform-appropriate bundled NSTool executable (`nstool.exe` on Windows, `nstool` on macOS/POSIX) or accept an explicit executable path, and return actionable diagnostics for executable or extraction failures.

#### Scenario: Refuse a non-empty destination by default
- **WHEN** a user selects an output directory that already contains files without an overwrite option
- **THEN** the CLI exits nonzero without invoking `nstool` and preserves the destination contents

#### Scenario: Accept an explicit overwrite request
- **WHEN** a user selects a non-empty output directory with the overwrite option
- **THEN** the CLI permits `nstool` to write the requested extraction there

#### Scenario: Discover bundled executable on Windows
- **WHEN** the CLI resolves the bundled executable on a Windows host without an explicit `--nstool` override
- **THEN** the CLI searches for `nstool.exe` before falling back to `nstool` in the bundled search directory

#### Scenario: Discover bundled executable on macOS and POSIX systems
- **WHEN** the CLI resolves the bundled executable on macOS or POSIX systems without an explicit `--nstool` override
- **THEN** the CLI searches for `nstool` before falling back to `nstool.exe` in the bundled search directory

#### Scenario: Report a missing executable
- **WHEN** neither the bundled nor explicitly configured `nstool` executable is runnable
- **THEN** the CLI exits nonzero and explains how to supply a valid executable path

#### Scenario: Preserve an external-tool failure
- **WHEN** `nstool` terminates unsuccessfully
- **THEN** the CLI exits nonzero and shows the attempted operation together with the tool's diagnostic output

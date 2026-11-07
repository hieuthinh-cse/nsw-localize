"""Discovery and invocation helpers for the external NSTool executable."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


class NstoolError(RuntimeError):
    """Raised when NSTool cannot be located or used."""


class ValidationError(NstoolError):
    """Raised when a user-provided filesystem path is unsafe or unavailable."""


class NstoolProcessError(NstoolError):
    """Raised when NSTool terminates unsuccessfully."""


@dataclass(frozen=True)
class NstoolResult:
    """Captured output from a successful NSTool invocation."""

    stdout: str
    stderr: str


def build_nca_merge_args(
    base_nca_path: Path,
    patch_nca_path: Path,
    keyset_path: Path,
    output_directory: Path,
    *,
    tik_path: Optional[Path] = None,
) -> list[str]:
    """Build NSTool arguments for merging a base NCA and update NCA to extract RomFS (/1)."""
    return build_nca_extract_args(
        input_path=patch_nca_path,
        keyset_path=keyset_path,
        output_directory=output_directory,
        virtual_path="/1",
        tik_path=tik_path,
        base_nca_path=base_nca_path,
    )


def build_nsp_extract_args(input_path: Path, output_directory: Path) -> list[str]:
    """Build NSTool arguments for extracting an NSP's root filesystem."""
    return ["-x", "/", str(output_directory), str(input_path)]


def build_nca_extract_args(
    input_path: Path,
    keyset_path: Path,
    output_directory: Path,
    virtual_path: str,
    *,
    tik_path: Optional[Path] = None,
    base_nca_path: Optional[Path] = None,
) -> list[str]:
    """Build NSTool arguments for extracting one NCA virtual path."""
    args = ["-k", str(keyset_path)]
    if tik_path is not None:
        args.extend(["--tik", str(tik_path)])
    if base_nca_path is not None:
        args.extend(["--basenca", str(base_nca_path)])
    args.extend(["-x", virtual_path, str(output_directory), str(input_path)])
    return args


def run_nstool(executable: Path, arguments: Sequence[str], *, operation: str) -> NstoolResult:
    """Run NSTool without a shell and return its captured output.

    Error messages deliberately omit command arguments because a keyset path may
    be sensitive. NSTool's own diagnostic remains available to the caller.
    """
    completed = subprocess.run(
        [str(executable), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or completed.stdout.strip()
        if not diagnostic:
            diagnostic = "NSTool did not provide a diagnostic."
        raise NstoolProcessError(
            f"NSTool {operation} failed with exit code {completed.returncode}: {diagnostic}"
        )
    return NstoolResult(stdout=completed.stdout, stderr=completed.stderr)


def validate_input_file(path: Path, label: str, suffix: Optional[str] = None) -> Path:
    """Validate and resolve a readable regular input file."""
    candidate = path.expanduser()
    if not candidate.is_file():
        raise ValidationError(f"{label} must be an existing regular file: {candidate}")
    if suffix is not None and candidate.suffix.lower() != suffix.lower():
        raise ValidationError(f"{label} must use the {suffix} extension: {candidate}")
    if not os.access(candidate, os.R_OK):
        raise ValidationError(f"{label} is not readable: {candidate}")
    return candidate.resolve()


def prepare_output_directory(path: Path, *, overwrite: bool) -> Path:
    """Create or validate a destination without silently replacing its contents."""
    candidate = path.expanduser()
    if candidate.exists() and not candidate.is_dir():
        raise ValidationError(f"Output path must be a directory: {candidate}")
    if candidate.is_dir() and any(candidate.iterdir()) and not overwrite:
        raise ValidationError(
            f"Output directory is not empty: {candidate}. Use --overwrite to allow writing there."
        )
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate.resolve()


def resolve_keyset(override: Optional[Path] = None) -> Path:
    """Resolve a readable keyset file from an override or ~/.switch/prod.keys."""
    if override is not None:
        return validate_input_file(override, "Keyset")
    default_keyset = Path("~/.switch/prod.keys").expanduser()
    if not default_keyset.is_file() or not os.access(default_keyset, os.R_OK):
        raise ValidationError(
            "Keyset not found. Provide a keyset with --keyset or place prod.keys at ~/.switch/prod.keys."
        )
    return default_keyset.resolve()


def is_executable_file(path: Path) -> bool:
    """Check whether a path points to an executable regular file."""
    if not path.is_file():
        return False
    if sys.platform == "win32":
        # On Windows, os.access(..., os.X_OK) checks extensions in PATHEXT
        # or may return true for readable files. Verify X_OK or known executable suffix.
        return path.suffix.lower() == ".exe" or os.access(path, os.X_OK)
    return os.access(path, os.X_OK)


def resolve_nstool(
    override: Optional[Path] = None, *, repository_root: Optional[Path] = None
) -> Path:
    """Return a runnable NSTool executable from an override or project root.

    An override is intentional and never falls back to the bundled executable:
    a spelling mistake in ``--nstool`` must be reported rather than hidden.
    When no override is provided, selects the appropriate bundled binary for
    the current operating system (nstool.exe on Windows, nstool on macOS/POSIX),
    falling back to the other candidate if present.
    """
    if override is not None:
        candidate = override.expanduser()
        if not candidate.is_file():
            raise NstoolError(
                "Unable to find a runnable NSTool executable at "
                f"{candidate}. Provide a compatible executable with --nstool "
                "(looked for --nstool path)."
            )
        if not is_executable_file(candidate):
            raise NstoolError(
                f"NSTool executable is not runnable: {candidate}. "
                "Grant execute permission or provide a compatible executable with --nstool."
            )
        return candidate.resolve()

    search_dir = (repository_root or Path.cwd()).expanduser()
    if sys.platform == "win32":
        candidates = ["nstool.exe", "nstool"]
    else:
        candidates = ["nstool", "nstool.exe"]

    for name in candidates:
        candidate = search_dir / name
        if candidate.is_file():
            if not is_executable_file(candidate):
                raise NstoolError(
                    f"NSTool executable is not runnable: {candidate}. "
                    "Grant execute permission or provide a compatible executable with --nstool."
                )
            return candidate.resolve()

    primary_target = search_dir / candidates[0]
    raise NstoolError(
        "Unable to find a runnable NSTool executable at "
        f"{primary_target}. Provide a compatible executable with --nstool "
        f"(looked for bundled {candidates[0]})."
    )

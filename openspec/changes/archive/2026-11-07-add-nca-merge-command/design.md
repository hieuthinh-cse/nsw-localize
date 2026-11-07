# Design: NCA Merge Command via NSTool

## Overview

The `merge-nca` command enables developers and translators to extract a fully patched RomFS directly from a base Program NCA and an update Program NCA using `nstool`.

## Command Line Interface

```sh
uv run nsw-unpack merge-nca \
  --base <path/to/base.nca> \
  --patch <path/to/update.nca> \
  --output <path/to/output_directory> \
  [--keyset <path/to/prod.keys>] \
  [--tik <path/to/patch.tik>] \
  [--nstool <path/to/nstool>] \
  [--overwrite]
```

### Options:
- `--base`: Path to the base Program NCA (required). Must be an existing, readable file with `.nca` extension.
- `--patch`: Path to the update Program NCA (required). Must be an existing, readable file with `.nca` extension.
- `--output`: Destination directory for the merged RomFS (required). Must be empty unless `--overwrite` is specified.
- `--keyset`: Keyset file (optional). If omitted, falls back to `~/.switch/prod.keys`. If that file does not exist, an actionable `ValidationError` is raised.
- `--tik`: Optional ticket file for title key decryption.
- `--nstool`: Optional path to custom `nstool` executable (defaults to repository `./nstool`).
- `--overwrite`: Allow extracting into a non-empty destination directory.

## Implementation Details

### 1. Keyset Resolution Helper (`nstool.py`)
Add `resolve_keyset(override: Optional[Path] = None) -> Path`:
- If `override` is provided, validate with `validate_input_file(override, "Keyset")`.
- Else check `Path("~/.switch/prod.keys").expanduser()`. If valid and readable, return resolved path.
- Else raise `ValidationError` prompting the user to supply `--keyset` or place keys in `~/.switch/prod.keys`.

### 2. Argument Construction (`nstool.py`)
Add `build_nca_merge_args`:
```python
def build_nca_merge_args(
    base_nca_path: Path,
    patch_nca_path: Path,
    keyset_path: Path,
    output_directory: Path,
    *,
    tik_path: Optional[Path] = None,
) -> list[str]:
    return build_nca_extract_args(
        input_path=patch_nca_path,
        keyset_path=keyset_path,
        output_directory=output_directory,
        virtual_path="/1",
        tik_path=tik_path,
        base_nca_path=base_nca_path,
    )
```

### 3. CLI Subcommand Handler (`cli.py`)
Add `_extract_merged_nca(arguments: argparse.Namespace)`:
1. Validate `--base` via `validate_input_file(arguments.base, "Base NCA input", ".nca")`.
2. Validate `--patch` via `validate_input_file(arguments.patch, "Patch NCA input", ".nca")`.
3. Resolve keyset via `resolve_keyset(arguments.keyset)`.
4. Validate `--tik` if provided via `validate_input_file(arguments.tik, "Ticket")`.
5. Prepare output directory with overwrite check.
6. Resolve `nstool` executable.
7. Run `nstool` with arguments from `build_nca_merge_args`.
8. Print clear success message.

## Error Handling & Diagnostics

- Missing or non-`.nca` files fail with `ValidationError` before running external tools.
- Keyset resolution failure clearly explains where it looked.
- Failed `nstool` subprocess propagates diagnostic text with non-zero exit code.

"""Project workspace resolution, initialization, and validation."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import yaml


class ProjectError(Exception):
    """Base exception for project management errors."""


class InvalidProjectNameError(ProjectError):
    """Raised when a submitted project name is empty, invalid, or unsafe."""


class ProjectExistsError(ProjectError):
    """Raised when a project directory already exists."""


def normalize_project_slug(name: str) -> str:
    """Normalize a submitted project name to a lowercase ASCII hyphenated slug.

    Rejects path separators, traversal components, and names that have no
    alphanumeric ASCII characters.
    """
    if not name or not name.strip():
        raise InvalidProjectNameError("Project name must not be empty.")

    if "/" in name or "\\" in name:
        raise InvalidProjectNameError("Project name must not contain path separators.")

    trimmed = name.strip()
    if trimmed in {".", ".."}:
        raise InvalidProjectNameError("Project name must not be a relative path component.")

    # Match alphanumeric ASCII tokens
    tokens = re.findall(r"[a-zA-Z0-9]+", trimmed)
    if not tokens:
        raise InvalidProjectNameError(
            "Project name must contain at least one alphanumeric character."
        )

    slug = "-".join(t.lower() for t in tokens)
    if not slug:
        raise InvalidProjectNameError("Project name normalized to an empty slug.")

    return slug


def resolve_project_path(projects_root: Path, name: str) -> tuple[str, Path]:
    """Resolve and validate a project name against the projects root directory.

    Returns a tuple of (slug, project_dir).
    """
    root = projects_root.resolve()
    slug = normalize_project_slug(name)

    project_dir = (root / slug).resolve()

    # Ensure the resolved path stays strictly within projects_root and directly under it
    try:
        relative = project_dir.relative_to(root)
    except ValueError as exc:
        raise InvalidProjectNameError("Project path escapes the projects root directory.") from exc

    if len(relative.parts) != 1 or relative.parts[0] != slug:
        raise InvalidProjectNameError("Project path resolution resulted in an invalid path.")

    return slug, project_dir


def build_workflow_manifest(project_name: str, forum_post_id: int) -> dict[str, Any]:
    """Generate workflow manifest dictionary for a project."""
    if not isinstance(forum_post_id, int) or isinstance(forum_post_id, bool) or forum_post_id <= 0:
        raise ProjectError("forum_post_id must be a positive integer.")

    return {
        "name": project_name.strip(),
        "version": 1,
        "forum_post_id": forum_post_id,
        "game": {
            "input": [
                {"base": "./rom/base/"},
                {"update": "./rom/update/"},
            ],
            "output": "./output/",
        },
    }


def create_project_workspace(
    projects_root: Path,
    name: str,
    forum_post_id: int,
) -> Path:
    """Create a new project workspace beneath projects_root.

    Initializes:
    - workflow.yaml
    - rom/base/
    - rom/update/
    - output/

    Raises:
    - InvalidProjectNameError: if the name is invalid or resolves outside projects_root.
    - ProjectExistsError: if the project directory already exists.
    - ProjectError: if creation fails unexpectedly.
    """
    slug, project_dir = resolve_project_path(projects_root, name)

    if project_dir.exists():
        raise ProjectExistsError(f"Project '{slug}' already exists.")

    created_root = False
    try:
        # Create project root; ensure parent projects_root exists
        project_dir.mkdir(parents=True, exist_ok=False)
        created_root = True

        (project_dir / "rom" / "base").mkdir(parents=True, exist_ok=True)
        (project_dir / "rom" / "update").mkdir(parents=True, exist_ok=True)
        (project_dir / "output").mkdir(parents=True, exist_ok=True)

        manifest = build_workflow_manifest(name, forum_post_id=forum_post_id)
        manifest_path = project_dir / "workflow.yaml"
        manifest_text = yaml.safe_dump(manifest, sort_keys=False)
        manifest_path.write_text(manifest_text, encoding="utf-8")
        return project_dir
    except FileExistsError as exc:
        raise ProjectExistsError(f"Project '{slug}' already exists.") from exc
    except Exception as exc:
        if created_root:
            shutil.rmtree(project_dir, ignore_errors=True)
        if isinstance(exc, ProjectError):
            raise
        raise ProjectError(f"Failed to create workspace: {exc}") from exc


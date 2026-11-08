"""Pure authorization policy for project management bot commands."""

from __future__ import annotations

from typing import Collection, Iterable


def is_authorized_to_create_project(
    *,
    is_administrator: bool,
    member_role_ids: Iterable[int],
    allowed_role_ids: Collection[int],
) -> bool:
    """Evaluate whether a member is allowed to create a project workspace.

    Access is granted if:
    1. The member has Discord Administrator permission.
    2. The member holds at least one role specified in allowed_role_ids.

    Otherwise access is denied.
    """
    if is_administrator:
        return True

    allowed_set = set(allowed_role_ids)
    if not allowed_set:
        return False

    return any(role_id in allowed_set for role_id in member_role_ids)

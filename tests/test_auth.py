"""Unit tests for the pure authorization policy."""

from __future__ import annotations

import unittest

from nsw_localize.auth import is_authorized_to_create_project


class TestAuthorization(unittest.TestCase):
    def test_administrator_granted_without_roles(self) -> None:
        self.assertTrue(
            is_authorized_to_create_project(
                is_administrator=True,
                member_role_ids=[],
                allowed_role_ids=[100, 200],
            )
        )

    def test_administrator_granted_even_if_allowed_roles_empty(self) -> None:
        self.assertTrue(
            is_authorized_to_create_project(
                is_administrator=True,
                member_role_ids=[],
                allowed_role_ids=[],
            )
        )

    def test_member_with_matching_role_granted(self) -> None:
        self.assertTrue(
            is_authorized_to_create_project(
                is_administrator=False,
                member_role_ids=[10, 200, 30],
                allowed_role_ids=[100, 200],
            )
        )

    def test_member_without_matching_role_denied(self) -> None:
        self.assertFalse(
            is_authorized_to_create_project(
                is_administrator=False,
                member_role_ids=[10, 20, 30],
                allowed_role_ids=[100, 200],
            )
        )

    def test_member_with_no_roles_denied(self) -> None:
        self.assertFalse(
            is_authorized_to_create_project(
                is_administrator=False,
                member_role_ids=[],
                allowed_role_ids=[100, 200],
            )
        )

    def test_member_denied_when_allowed_roles_empty(self) -> None:
        self.assertFalse(
            is_authorized_to_create_project(
                is_administrator=False,
                member_role_ids=[10, 20],
                allowed_role_ids=[],
            )
        )


if __name__ == "__main__":
    unittest.main()

"""Mock repository standing in for a real `UserRoles` database table."""

_MOCK_USER_ROLES: dict[str, str] = {
    "reader_user": "read_only_role",
    "working_user": "read_write_role",
    "working_admin_user": "admin_role",
}


class UserRoleRepository:
    def get_role_for_user(self, user_id: str | None) -> str | None:
        if user_id is None:
            return None
        return _MOCK_USER_ROLES.get(user_id)

from pilot_api.security.role_repository import UserRoleRepository


def test_known_users_resolve_expected_roles() -> None:
    repository = UserRoleRepository()

    assert repository.get_role_for_user("reader_user") == "read_only_role"
    assert repository.get_role_for_user("working_user") == "read_write_role"
    assert repository.get_role_for_user("working_admin_user") == "admin_role"


def test_unknown_or_missing_user_resolves_to_none() -> None:
    repository = UserRoleRepository()

    assert repository.get_role_for_user("nobody") is None
    assert repository.get_role_for_user(None) is None

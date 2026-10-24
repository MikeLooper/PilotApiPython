import pytest
from pydantic import ValidationError

from pilot_api.config.settings import Settings


def test_resolved_public_issuer_url_falls_back_to_base_url_when_unset() -> None:
    settings = Settings(
        identity_provider_base_url="http://localhost:11141",
        identity_provider_public_base_url=None,
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "http://localhost:11141/realms/local-realm"


def test_resolved_public_issuer_url_uses_public_base_url_when_set() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:11141",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "http://localhost:11141/realms/local-realm"


def test_resolved_public_issuer_url_uses_full_override_when_set() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:11141",
        identity_provider_public_issuer_url="https://override.test/realms/other-realm",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "https://override.test/realms/other-realm"


def test_resolved_issuer_url_is_independent_of_public_base_url() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:11141",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_issuer_url == "http://local-keycloak:8080/realms/local-realm"


def test_sqlserver_is_default_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_BACKEND", raising=False)

    settings = Settings(_env_file=None, db_password="secret")

    assert settings.db_backend == "sqlserver"
    assert settings.resolved_database_url.startswith("mssql+pyodbc://")


def test_postgresql_backend_uses_postgres_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_BACKEND", "postgresql")

    settings = Settings(_env_file=None, db_password="secret")

    assert settings.db_backend == "postgresql"
    assert settings.resolved_database_url.startswith("postgresql+psycopg://")
    assert "northwind" in settings.resolved_database_url
    assert "pilot" in settings.resolved_database_url


def test_fails_fast_when_neither_database_url_nor_db_password_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(ValidationError, match="DATABASE_URL or DB_PASSWORD"):
        Settings(_env_file=None)


def test_secrets_are_not_exposed_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(_env_file=None, db_password="TopSecret!")

    assert "TopSecret!" not in repr(settings)
    assert "TopSecret%21" in settings.resolved_database_url


def test_secure_and_anonymous_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "DB_TRUST_SERVER_CERTIFICATE",
        "APP_CONTACT_NAME",
        "APP_CONTACT_EMAIL",
        "APP_CONTACT_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings(_env_file=None)

    assert settings.db_trust_server_certificate is False
    assert settings.app_contact_name is None
    assert settings.app_contact_email is None
    assert settings.app_contact_url is None

from pilot_api.config.settings import Settings


def test_resolved_public_issuer_url_falls_back_to_base_url_when_unset() -> None:
    settings = Settings(
        identity_provider_base_url="http://localhost:55001",
        identity_provider_public_base_url=None,
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "http://localhost:55001/realms/local-realm"


def test_resolved_public_issuer_url_uses_public_base_url_when_set() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:55001",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "http://localhost:55001/realms/local-realm"


def test_resolved_public_issuer_url_uses_full_override_when_set() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:55001",
        identity_provider_public_issuer_url="https://override.test/realms/other-realm",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_public_issuer_url == "https://override.test/realms/other-realm"


def test_resolved_issuer_url_is_independent_of_public_base_url() -> None:
    settings = Settings(
        identity_provider_base_url="http://local-keycloak:8080",
        identity_provider_public_base_url="http://localhost:55001",
        identity_provider_realm="local-realm",
    )

    assert settings.resolved_issuer_url == "http://local-keycloak:8080/realms/local-realm"

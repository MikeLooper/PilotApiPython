from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PilotApiPython"
    app_version: str = "1.0.0"
    app_deploy_date: str | None = None
    app_description: str = (
        "A proof of concept API to explore best-practices and new ideas, based upon the "
        "Northwind database."
    )
    app_summary: str = "Proof of concept API for the Northwind database."
    app_contact_name: str = "Michael Looper"
    app_contact_email: str = "MikelLooper@gmail.com"
    app_contact_url: str = "https://github.com/MikeLooper"
    app_license_name: str = "MIT"
    app_license_url: str = "https://opensource.org"
    log_level: str = "INFO"
    log_json: bool = True
    show_about_config: bool = True

    db_backend: str = "sqlserver"
    db_name: str = "NorthWind"
    db_connect_timeout: int = 30
    db_host: str = "local_mssql"
    db_password: str = "<DevUser password>"
    db_port: int = 1433
    db_schema: str = "dbo"
    db_user: str = "DevUser"
    db_driver: str = "ODBC Driver 18 for SQL Server"
    db_trust_server_certificate: bool = True

    # Optional full override. If supplied, this value is used as-is.
    database_url: str | None = None

    security_active: bool = True

    # Reachable directly from this API, for fetching signing keys (e.g. "http://local-keycloak:8080"
    # when both run on the same Docker network).
    identity_provider_base_url: str = "http://local-keycloak:8080"
    # Externally-visible base URL, i.e. the one clients use to obtain tokens (e.g.
    # "http://localhost:55001"). Tokens carry this value as their issuer, so it is what
    # resolved_public_issuer_url validates against.
    identity_provider_public_base_url: str | None = "http://localhost:55001"
    identity_provider_realm: str = "local-realm"
    identity_provider_client_id: str = "local-client"
    identity_provider_audience: str | None = None
    jwks_cache_seconds: int = 3600

    # Optional full overrides. If supplied, these values are used as-is.
    identity_provider_issuer_url: str | None = None
    identity_provider_public_issuer_url: str | None = None
    identity_provider_jwks_url: str | None = None

    @field_validator(
        "identity_provider_audience",
        "identity_provider_public_base_url",
        "identity_provider_issuer_url",
        "identity_provider_public_issuer_url",
        "identity_provider_jwks_url",
        mode="before",
    )
    @classmethod
    def _blank_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def resolved_issuer_url(self) -> str:
        if self.identity_provider_issuer_url:
            return self.identity_provider_issuer_url
        return f"{self.identity_provider_base_url}/realms/{self.identity_provider_realm}"

    @property
    def resolved_public_issuer_url(self) -> str:
        if self.identity_provider_public_issuer_url:
            return self.identity_provider_public_issuer_url
        base_url = self.identity_provider_public_base_url or self.identity_provider_base_url
        return f"{base_url}/realms/{self.identity_provider_realm}"

    @property
    def resolved_jwks_url(self) -> str:
        if self.identity_provider_jwks_url:
            return self.identity_provider_jwks_url
        return f"{self.resolved_issuer_url}/protocol/openid-connect/certs"

    @property
    def resolved_db_display_name(self) -> str:
        if self.db_backend.lower() == "postgresql":
            return "PostgreSQL"
        return "SQL Server"

    @property
    def resolved_db_name(self) -> str:
        if self.db_backend.lower() == "postgresql":
            return "northwind"
        return self.db_name

    @property
    def resolved_db_host(self) -> str:
        if self.db_backend.lower() == "postgresql":
            return "localhost" if self.db_host == "local_mssql" else self.db_host
        return self.db_host

    @property
    def resolved_db_port(self) -> int:
        if self.db_backend.lower() == "postgresql":
            return 5432 if self.db_port == 1433 else self.db_port
        return self.db_port

    @property
    def resolved_db_schema(self) -> str:
        if self.db_backend.lower() == "postgresql":
            return "pilot"
        return self.db_schema

    @property
    def resolved_db_user(self) -> str:
        if self.db_backend.lower() == "postgresql":
            return self.db_user or "DevUser"
        return self.db_user

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        encoded_password = quote_plus(self.db_password)

        if self.db_backend.lower() == "postgresql":
            return (
                f"postgresql+psycopg://{self.resolved_db_user}:{encoded_password}@{self.resolved_db_host}:{self.resolved_db_port}/{self.resolved_db_name}"
                f"?connect_timeout={self.db_connect_timeout}&options=-csearch_path%3D{self.resolved_db_schema}"
            )

        driver = quote_plus(self.db_driver)
        trust_server_certificate = "yes" if self.db_trust_server_certificate else "no"
        return (
            f"mssql+pyodbc://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?driver={driver}&TrustServerCertificate={trust_server_certificate}&timeout={self.db_connect_timeout}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()

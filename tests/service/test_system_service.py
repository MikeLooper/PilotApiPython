from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from pilot_api.config.settings import get_settings
from pilot_api.dto.schemas import DataSourceTypes
from pilot_api.service.system_service import SystemService


@pytest.fixture(autouse=True)
def _fresh_settings() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_healthcheck_returns_ok(db_session: Session) -> None:
    assert SystemService(session=db_session).healthcheck() == "OK"


def test_about_includes_config_when_show_details_true_and_enabled(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")
    monkeypatch.setenv("APP_VERSION", "1.0.0")
    monkeypatch.setenv("APP_LICENSE_NAME", "Apache-2.0")
    monkeypatch.setenv("DB_BACKEND", "sqlserver")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_NAME", "NorthWind")

    result = SystemService(session=db_session).about(show_details=True)

    config = result.applicationConfiguration
    assert config is not None
    assert config.active is True
    assert config.dataConnections is not None
    assert config.dataConnections[0].host == "localhost"
    assert config.dataConnections[0].dataSourceName == "sqlserver"
    assert config.dataSources is not None
    assert config.dataSources[0].dataSource == "NorthWind"
    assert config.dataSources[0].dataSourceName == "sqlserver"
    assert config.dataSources[0].dataSourceEnum == DataSourceTypes.SQLSERVER
    assert config.dataSources[0].dataSourceType == "SqlServer"
    assert config.openApi is not None
    assert config.openApi.title == "PilotApiPython"
    assert config.openApi.version == "1.0.0"
    assert config.openApi.license == "Apache-2.0"


def test_about_config_never_exposes_database_credentials(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")

    result = SystemService(session=db_session).about(show_details=True)

    dumped = result.model_dump_json(by_alias=True)
    assert "userName" not in dumped
    assert "password" not in dumped


def test_about_config_includes_security_and_open_telemetry(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")
    monkeypatch.setenv("SECURITY_ACTIVE", "false")
    monkeypatch.setenv("IDENTITY_PROVIDER_BASE_URL", "http://idp:8080")
    monkeypatch.setenv("IDENTITY_PROVIDER_REALM", "test-realm")
    monkeypatch.setenv("IDENTITY_PROVIDER_CLIENT_ID", "test-client")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")

    config = SystemService(session=db_session).about(show_details=True).applicationConfiguration

    assert config is not None
    assert config.security is not None
    assert config.security.active is False
    assert config.security.baseUrl == "http://idp:8080"
    assert config.security.realm == "test-realm"
    assert config.security.clientId == "test-client"
    assert config.security.authority == "http://idp:8080/realms/test-realm"
    assert config.openTelemetry is not None
    assert config.openTelemetry.server == "collector"
    assert config.openTelemetry.port == 4317


def test_about_config_reports_postgresql_data_source_type(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")
    monkeypatch.setenv("DB_BACKEND", "postgresql")

    config = SystemService(session=db_session).about(show_details=True).applicationConfiguration

    assert config is not None
    assert config.dataSources is not None
    assert config.dataSources[0].dataSourceEnum == DataSourceTypes.POSTGRESQL
    assert config.dataSources[0].dataSourceType == "PostgreSQL"


def test_about_omits_config_when_show_about_config_false(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "false")

    result = SystemService(session=db_session).about(show_details=True)

    assert result.applicationConfiguration is None


def test_about_omits_config_when_show_details_false(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")

    result = SystemService(session=db_session).about(show_details=False)

    assert result.applicationConfiguration is None


def test_about_uses_build_supplied_deploy_date_and_build_version(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    deploy_date = "2026-08-16T09:00:00+00:00"
    monkeypatch.setenv("APP_DEPLOY_DATE", deploy_date)
    monkeypatch.setenv("APP_BUILD_VERSION", "1.2.3+build.45")

    result = SystemService(session=db_session).about(show_details=False)

    assert result.deployDate == deploy_date
    assert result.buildVersion == "1.2.3+build.45"


def test_about_falls_back_to_stable_start_time_and_app_version(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APP_DEPLOY_DATE", raising=False)
    monkeypatch.delenv("APP_BUILD_VERSION", raising=False)
    monkeypatch.setenv("APP_VERSION", "9.9.9")

    first = SystemService(session=db_session).about(show_details=False)
    second = SystemService(session=db_session).about(show_details=False)

    assert first.deployDate is not None
    assert first.deployDate == second.deployDate
    assert first.buildVersion == "9.9.9"

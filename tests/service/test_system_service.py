from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pilot_api.config.settings import get_settings
from pilot_api.model.base import Base
from pilot_api.service.system_service import SystemService


def test_system_service_healthcheck_returns_ok() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        get_settings.cache_clear()
        service = SystemService(session=session)

        result = service.healthcheck()

        assert result == "OK"
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_system_service_about_includes_config_when_show_details_true(monkeypatch) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "false")
    get_settings.cache_clear()

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        service = SystemService(session=session)

        result = service.about(show_details=True)

        assert result.applicationConfiguration is not None
        assert result.applicationConfiguration.active is True
        assert result.applicationConfiguration.dataSources is not None
        assert result.applicationConfiguration.dataSources[0].dataSource == "NorthWind"
        assert result.applicationConfiguration.dataSources[0].host == "localhost"
        assert result.applicationConfiguration.dataSources[0].password is None
        assert result.applicationConfiguration.openApi is not None
        assert result.applicationConfiguration.openApi.title == "PilotApiPython"
        assert result.applicationConfiguration.openApi.version == "1.0.0"
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        get_settings.cache_clear()


def test_system_service_about_uses_app_deploy_date(monkeypatch) -> None:
    deploy_date = "2026-08-16T09:00:00+00:00"
    monkeypatch.setenv("APP_DEPLOY_DATE", deploy_date)
    get_settings.cache_clear()

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        service = SystemService(session=session)

        result = service.about(show_details=False)

        assert result.deployDate == deploy_date
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        get_settings.cache_clear()


def test_system_service_about_omits_config_when_show_details_false(monkeypatch) -> None:
    monkeypatch.setenv("SHOW_ABOUT_CONFIG", "true")
    get_settings.cache_clear()

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        service = SystemService(session=session)

        result = service.about(show_details=False)

        assert result.applicationConfiguration is None
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        get_settings.cache_clear()

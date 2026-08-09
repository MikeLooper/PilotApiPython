from pilot_api.config.settings import Settings, clear_settings_cache


def test_sqlserver_is_default_backend(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_BACKEND", raising=False)
    clear_settings_cache()

    settings = Settings()

    assert settings.db_backend == "sqlserver"
    assert settings.resolved_database_url.startswith("mssql+pyodbc://")


def test_postgresql_backend_uses_postgres_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_BACKEND", "postgresql")
    clear_settings_cache()

    settings = Settings()

    assert settings.db_backend == "postgresql"
    assert settings.resolved_database_url.startswith("postgresql+psycopg://")
    assert "northwind" in settings.resolved_database_url
    assert "pilot" in settings.resolved_database_url

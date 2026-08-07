from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PilotApiPython"
    app_version: str = "1.0.0"
    app_description: str = (
        "A proof of concept API to explore best-practices and new ideas, based upon the "
        "Northwind database."
    )
    log_level: str = "INFO"
    log_json: bool = True
    show_about_config: bool = False

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

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        encoded_password = quote_plus(self.db_password)
        driver = quote_plus(self.db_driver)
        trust_server_certificate = "yes" if self.db_trust_server_certificate else "no"
        return (
            f"mssql+pyodbc://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?driver={driver}&TrustServerCertificate={trust_server_certificate}&timeout={self.db_connect_timeout}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

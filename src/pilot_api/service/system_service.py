from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.orm import Session

from pilot_api.config.settings import get_settings
from pilot_api.dto.schemas import (
    AboutResponseDto,
    ApplicationConfigurationDto,
    DataConnectionConfigurationDto,
    DataSourceConfigurationDto,
    DataSourceTypes,
    OpenApiConfigurationDto,
    OpenApiContactConfigurationDto,
    OpenTelemetryConfigurationDto,
    SecurityConfigurationDto,
)

# Fallback deployDate when the build does not supply APP_DEPLOY_DATE: captured
# once at import so /about reports a stable value for the life of the process.
_PROCESS_START_TIME = datetime.now(UTC).isoformat()

# The spec's string form of each data source type (e.g. "SqlServer", "PostgreSQL").
_DATA_SOURCE_TYPE_NAMES = {
    DataSourceTypes.POSTGRESQL: "PostgreSQL",
    DataSourceTypes.SQLSERVER: "SqlServer",
}


def _data_source_enum(db_backend: str) -> DataSourceTypes:
    match db_backend.lower():
        case "postgresql":
            return DataSourceTypes.POSTGRESQL
        case "sqlserver":
            return DataSourceTypes.SQLSERVER
        case _:
            return DataSourceTypes.UNRECOGNIZED


class SystemService:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def healthcheck(self) -> str:
        self.session.execute(text("SELECT 1"))
        return "OK"

    def about(self, show_details: bool) -> AboutResponseDto:
        config = None
        if show_details and self.settings.show_about_config:
            settings = self.settings
            data_source_enum = _data_source_enum(settings.db_backend)
            data_source_name = settings.db_backend
            otel_endpoint = urlparse(settings.otel_exporter_otlp_endpoint)
            config = ApplicationConfigurationDto(
                active=True,
                dataConnections=[
                    DataConnectionConfigurationDto(
                        active=True,
                        connectTimeout=settings.db_connect_timeout,
                        dataSourceName=data_source_name,
                        host=settings.resolved_db_host,
                        port=settings.resolved_db_port,
                    )
                ],
                dataSources=[
                    DataSourceConfigurationDto(
                        active=True,
                        dataSource=settings.resolved_db_name,
                        dataSourceEnum=data_source_enum,
                        dataSourceName=data_source_name,
                        dataSourceType=_DATA_SOURCE_TYPE_NAMES.get(
                            data_source_enum, settings.db_backend
                        ),
                        schema_=settings.resolved_db_schema,
                    )
                ],
                security=SecurityConfigurationDto(
                    active=settings.security_active,
                    baseUrl=settings.identity_provider_base_url,
                    realm=settings.identity_provider_realm,
                    clientId=settings.identity_provider_client_id,
                    # TokenValidator neither enforces HTTPS for JWKS nor applies clock-skew leeway.
                    requireHttpsMetadata=False,
                    clockSkewSeconds=0,
                    authority=settings.resolved_issuer_url,
                ),
                openApi=OpenApiConfigurationDto(
                    active=True,
                    contact=OpenApiContactConfigurationDto(
                        active=True,
                        email=settings.app_contact_email,
                        name=settings.app_contact_name,
                        url=settings.app_contact_url,
                    ),
                    description=settings.app_description,
                    license=settings.app_license_name,
                    summary=settings.app_summary,
                    title=settings.app_name,
                    version=settings.app_version,
                ),
                openTelemetry=OpenTelemetryConfigurationDto(
                    active=settings.otel_enabled,
                    server=otel_endpoint.hostname,
                    port=otel_endpoint.port,
                ),
            )
        return AboutResponseDto(
            apiVersion=self.settings.app_version,
            buildVersion=self.settings.app_build_version or self.settings.app_version,
            deployDate=self.settings.app_deploy_date or _PROCESS_START_TIME,
            name=f"{self.settings.app_name} ({self.settings.resolved_db_display_name})",
            applicationConfiguration=config,
        )

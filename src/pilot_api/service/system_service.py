from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from pilot_api.config.settings import get_settings
from pilot_api.dto.schemas import (
    AboutResponseDto,
    ApplicationConfigurationDto,
    DataSourceConfigurationDto,
    OpenApiConfigurationDto,
)


class SystemService:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def healthcheck(self) -> str:
        self.session.execute(text("SELECT 1"))
        return "OK"

    def about(self, show_details: bool) -> AboutResponseDto:
        config = None
        if show_details:
            config = ApplicationConfigurationDto(
                active=True,
                dataSources=[
                    DataSourceConfigurationDto(
                        active=True,
                        connectTimeout=self.settings.db_connect_timeout,
                        dataSource=self.settings.resolved_db_name,
                        dataSourceType=self.settings.db_backend,
                        host=self.settings.resolved_db_host,
                        port=self.settings.resolved_db_port,
                        schema_=self.settings.resolved_db_schema,
                        userName=self.settings.resolved_db_user,
                    )
                ],
                openApi=OpenApiConfigurationDto(
                    active=True,
                    description=self.settings.app_description,
                    title=self.settings.app_name,
                    version=self.settings.app_version,
                ),
            )
        return AboutResponseDto(
            apiVersion=self.settings.app_version,
            buildVersion=self.settings.app_version,
            deployDate=self.settings.app_deploy_date or datetime.now(UTC).isoformat(),
            name=f"{self.settings.app_name} ({self.settings.resolved_db_display_name})",
            applicationConfiguration=config,
        )

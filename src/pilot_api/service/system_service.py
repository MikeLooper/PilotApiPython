from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from pilot_api.config.settings import get_settings
from pilot_api.dto.schemas import AboutResponseDto, ApplicationConfigurationDto


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
            config = ApplicationConfigurationDto(active=True)
        return AboutResponseDto(
            apiVersion=self.settings.app_version,
            buildVersion=self.settings.app_version,
            deployDate=datetime.now(UTC).isoformat(),
            name=self.settings.app_name,
            applicationConfiguration=config,
        )

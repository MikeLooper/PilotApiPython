from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AboutMetadata:
    name: str
    api_version: str
    build_version: str
    deploy_date: datetime | None

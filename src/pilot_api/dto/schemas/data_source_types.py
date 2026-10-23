from enum import IntEnum


class DataSourceTypes(IntEnum):
    """Enums for the available data sources."""

    UNRECOGNIZED = 0
    POSTGRESQL = 1
    SQLSERVER = 2

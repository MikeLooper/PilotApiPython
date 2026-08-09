from fastapi import Header


async def get_api_version(api_version: str | None = Header(default=None, alias="ApiVersion")) -> str | None:
    return api_version

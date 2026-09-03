import logging
from functools import lru_cache

from fastapi import Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pilot_api.config.settings import Settings, get_settings
from pilot_api.exception.errors import ForbiddenError, UnauthorizedError
from pilot_api.security.context import SecurityContext
from pilot_api.security.role_repository import UserRoleRepository
from pilot_api.security.token_validator import TokenValidationError, TokenValidator

logger = logging.getLogger(__name__)

# Declared purely so FastAPI's OpenAPI generation records a `bearerAuth`
# security scheme and marks dependent routes as requiring it (lock icon in
# Swagger UI). Token extraction/validation itself still happens in
# SecurityHelper.enforce, which reads the raw header directly.
bearer_scheme = HTTPBearer(
    scheme_name="bearerAuth",
    description="JWT bearer token issued by the identity provider.",
    auto_error=False,
)

_ROLE_RANK = {"read_only_role": 1, "read_write_role": 2, "admin_role": 3}

_READ_METHODS = {"GET", "HEAD", "OPTIONS", "QUERY", "TRACE"}
_WRITE_METHODS = {"PATCH", "POST", "PUT"}
_ADMIN_METHODS = {"DELETE"}

# Note: FastAPI/Starlette do not route QUERY or TRACE today, so those entries
# exist for spec completeness but are not currently exercised by any route.
_METHOD_MIN_RANK = (
    {method: 1 for method in _READ_METHODS}
    | {method: 2 for method in _WRITE_METHODS}
    | {method: 3 for method in _ADMIN_METHODS}
)


def is_authorized(effective_role: str | None, method: str) -> bool:
    return _ROLE_RANK.get(effective_role, 0) >= _METHOD_MIN_RANK.get(method, 3)


def _extract_token_roles(claims: dict) -> frozenset[str]:
    roles = set(claims.get("realm_access", {}).get("roles", []) or [])
    for area_roles in (claims.get("resource_access", {}) or {}).values():
        roles.update(area_roles.get("roles", []) or [])
    return frozenset(roles)


def _extract_client_attributes(claims: dict) -> dict:
    return {key: claims[key] for key in ("azp", "resource_access", "client_id") if key in claims}


class SecurityHelper:
    """Centralizes authentication (JWT/JWKS) and authorization (role-based) logic."""

    def __init__(
        self,
        settings: Settings,
        token_validator: TokenValidator,
        role_repository: UserRoleRepository,
    ):
        self._settings = settings
        self._token_validator = token_validator
        self._role_repository = role_repository

    async def enforce(self, request: Request, response: Response) -> SecurityContext:
        raw_token = self._extract_bearer_token(request)
        try:
            context = self._authenticate(raw_token)
            self._authorize(context, request.method)
        except (UnauthorizedError, ForbiddenError) as exc:
            self._log_failure(exc.detail, request, raw_token)
            if self._settings.security_active:
                raise
            response.headers["Warning"] = f'299 pilot-api "{exc.detail}"'
            return SecurityContext.anonymous(exc.detail)

        self._log_success(context, request, raw_token)
        return context

    @staticmethod
    def _extract_bearer_token(request: Request) -> str | None:
        header = request.headers.get("Authorization")
        if not header or not header.lower().startswith("bearer "):
            return None
        token = header[len("Bearer ") :].strip()
        return token or None

    def _authenticate(self, raw_token: str | None) -> SecurityContext:
        if not raw_token:
            raise UnauthorizedError("Missing bearer token.")
        try:
            claims = self._token_validator.decode(raw_token)
        except TokenValidationError as exc:
            raise UnauthorizedError(f"Authentication failed: {exc.reason}") from exc

        user_id = claims.get("preferred_username") or claims.get("sub")
        effective_role = self._role_repository.get_role_for_user(user_id)

        return SecurityContext(
            is_authenticated=True,
            user_id=user_id,
            token_roles=_extract_token_roles(claims),
            scopes=frozenset((claims.get("scope") or "").split()),
            client_attributes=_extract_client_attributes(claims),
            effective_role=effective_role,
            claims=claims,
        )

    @staticmethod
    def _authorize(context: SecurityContext, method: str) -> None:
        if not is_authorized(context.effective_role, method):
            raise ForbiddenError(
                f"Role '{context.effective_role}' is not permitted to perform '{method}'."
            )

    def _log_success(
        self, context: SecurityContext, request: Request, raw_token: str | None
    ) -> None:
        logger.info(
            "Authentication succeeded user_id=%s effective_role=%s method=%s path=%s jwt=%s",
            context.user_id,
            context.effective_role,
            request.method,
            request.url.path,
            raw_token,
            extra=self._request_extra(request),
        )

    def _log_failure(self, reason: str, request: Request, raw_token: str | None) -> None:
        logger.warning(
            "Authentication/authorization failed reason=%s method=%s path=%s jwt=%s",
            reason,
            request.method,
            request.url.path,
            raw_token,
            extra=self._request_extra(request),
        )

    @staticmethod
    def _request_extra(request: Request) -> dict:
        return {
            "request_id": getattr(request.state, "request_id", "-"),
            "correlation_id": getattr(request.state, "correlation_id", "-"),
            "operation_id": request.url.path,
        }


@lru_cache(maxsize=1)
def get_security_helper() -> SecurityHelper:
    settings = get_settings()
    return SecurityHelper(
        settings=settings,
        token_validator=TokenValidator(
            jwks_url=settings.resolved_jwks_url,
            issuer=settings.resolved_issuer_url,
            audience=settings.identity_provider_audience,
            cache_seconds=settings.jwks_cache_seconds,
        ),
        role_repository=UserRoleRepository(),
    )


def clear_security_helper_cache() -> None:
    get_security_helper.cache_clear()


async def enforce_security(
    request: Request,
    response: Response,
    _credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    helper: SecurityHelper = Depends(get_security_helper),
) -> SecurityContext:
    return await helper.enforce(request, response)

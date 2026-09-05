# Add Security — Implementation Plan

## 1. Objective

Implement authentication and authorization on all domain (`/v1/...`) endpoints of this API, excluding the System endpoints (`/healthcheck`, `/about`). Authentication is JWT/OAuth2 against an external, self-hosted IDP (Keycloak, referred to generically in code/config). Authorization is role-based, driven by a mock `UserRoles` lookup. Both are centralized in a `SecurityHelper`, gated by an `active` flag, and fully covered by unit tests.

## 2. Scope

| In scope | Out of scope |
| --- | --- |
| All routers under `/v1` (12 resource routers: categories, customers, employees, orders, order-details, products, shippers, suppliers, and the currently-commented-out customer-demographics, customer-customer-demo, employee-territories, regions, territories) | `/healthcheck`, `/about` (System router) |
| JWT signature/issuer/expiry validation via JWKS | Standing up a real Keycloak instance (assumed already running per the URLs below) |
| Role-based authorization (read/write/admin tiers) | Fine-grained per-field or per-record authorization |
| Mock `UserRoles` repository | Wiring a real database-backed roles table |
| Structured auth logging with redaction | Editing the shared `PilotApi_v1.yaml` OpenAPI contract (submodule) — see [§14 Follow-ups](#14-out-of-scope--follow-ups) |

## 3. Architecture Overview

New `security` package, parallel to the existing `config`, `api`, `dto`, `service`, `repository`, `exception` packages:

```
src/pilot_api/security/
    __init__.py
    context.py           # SecurityContext (the enriched "context User")
    role_repository.py   # UserRoleRepository (mock UserRoles table)
    token_validator.py   # JWKS fetch + JWT decode/verify
    security_helper.py   # SecurityHelper: centralizes auth + authz + logging
```

Modified existing files:

```
src/pilot_api/config/settings.py          # new security/IDP settings
src/pilot_api/config/logging_config.py    # secret-redaction log filter
src/pilot_api/exception/errors.py         # UnauthorizedError, ForbiddenError
src/pilot_api/api/routes/v1/__init__.py   # wire SecurityHelper.enforce as a router dependency
.env.example                              # new env vars (both DB profiles)
README.md                                 # "Security" usage section
pyproject.toml                            # add pyjwt[crypto]
```

Why a single router-level dependency instead of touching all 12 route files: `resources_router` (all domain endpoints) is already assembled independently of `system_router` in [router.py](src/pilot_api/api/router.py) / [v1/__init__.py](src/pilot_api/api/routes/v1/__init__.py). Attaching the dependency once, where `resources_router` is included, covers every current and future domain endpoint — including the hand-written composite-key routes (e.g. `order_details.py`) that don't go through the `register_single_key_routes` factory — without editing any of the 12 resource files individually.

## 4. Configuration

Add to [settings.py](src/pilot_api/config/settings.py), following the existing property-resolution pattern used for `db_*`/`resolved_db_*`:

```python
security_active: bool = True

identity_provider_base_url: str = "http://local-keycloak:8080"
identity_provider_realm: str = "local-realm"
identity_provider_client_id: str = "local-client"
identity_provider_audience: str | None = None   # None => skip audience check
jwks_cache_seconds: int = 3600

# Optional full overrides, same escape hatch as `database_url`
identity_provider_issuer_url: str | None = None
identity_provider_jwks_url: str | None = None

@property
def resolved_issuer_url(self) -> str:
    if self.identity_provider_issuer_url:
        return self.identity_provider_issuer_url
    return f"{self.identity_provider_base_url}/realms/{self.identity_provider_realm}"

@property
def resolved_jwks_url(self) -> str:
    if self.identity_provider_jwks_url:
        return self.identity_provider_jwks_url
    return f"{self.resolved_issuer_url}/protocol/openid-connect/certs"
```

The default `identity_provider_base_url` mirrors the existing `db_host` convention: it defaults to the Docker-network hostname (`local-keycloak`, production-style), and local development overrides it to `http://localhost:55001` via `.env`. No setting, class, or variable name contains the word `Keycloak` (per the vendor-neutrality requirement) — the value itself may point at a Keycloak instance, but nothing in the code or config *names* it.

`.env.example` additions (both the SQL Server and PostgreSQL blocks in the README get the same lines):

```
SECURITY_ACTIVE=true
IDENTITY_PROVIDER_BASE_URL=http://localhost:55001
IDENTITY_PROVIDER_REALM=local-realm
IDENTITY_PROVIDER_CLIENT_ID=local-client
IDENTITY_PROVIDER_AUDIENCE=
```

## 5. Authentication Design

Dependency: `pyjwt[crypto]>=2.9.0,<3.0.0`. It ships `jwt.PyJWKClient`, which fetches, verifies (`kid`-matched), and caches signing keys from a JWKS endpoint — no need to hand-roll caching or a Keycloak-specific SDK, keeping the vendor-neutral requirement intact.

`token_validator.py`:

```python
class TokenValidationError(Exception):
    def __init__(self, reason: str): ...

class TokenValidator:
    def __init__(self, jwks_url: str, issuer: str, audience: str | None, cache_seconds: int):
        self._jwk_client = jwt.PyJWKClient(jwks_url, lifespan=cache_seconds)
        ...

    def decode(self, raw_token: str) -> dict[str, Any]:
        # 1. resolve signing key via self._jwk_client.get_signing_key_from_jwt(raw_token)
        # 2. jwt.decode(raw_token, key, algorithms=["RS256"], issuer=self._issuer,
        #      audience=self._audience, options={"verify_aud": self._audience is not None})
        # 3. wrap PyJWKClientError / jwt.PyJWTError -> TokenValidationError(reason)
```

`TokenValidator` takes the JWKS client as an injectable collaborator so tests can substitute a fake key resolver and never hit the network (see [§12 Testing](#12-testing-plan)).

Flow driven by `SecurityHelper`:
1. Read `Authorization` header. Missing or not `Bearer <token>` → `TokenValidationError("missing bearer token")`.
2. `TokenValidator.decode(token)` → verified claims, or `TokenValidationError` with a specific reason (expired, bad signature, wrong issuer/audience, malformed).
3. Claims are hydrated into a `SecurityContext` (§6).

## 6. Authorization Design

### 6.1 `SecurityContext` (the enriched "context User")

`context.py`:

```python
@dataclass(frozen=True)
class SecurityContext:
    is_authenticated: bool
    user_id: str | None
    token_roles: frozenset[str]        # realm_access.roles ∪ every resource_access.<area>.roles
    scopes: frozenset[str]             # split "scope" claim
    client_attributes: dict[str, Any]  # azp, resource_access, and other non-standard claims
    effective_role: str | None         # resolved via UserRoleRepository
    claims: dict[str, Any]             # full decoded token, for anything else callers need
    auth_failure_reason: str | None = None

    @classmethod
    def anonymous(cls, reason: str) -> "SecurityContext": ...
```

This satisfies "enrich the context User so authentication and authorization code can see role, claim, and scope data from the security token" — `token_roles`, `scopes`, and `client_attributes` all come straight off the token, independent of the RBAC decision below.

### 6.2 Role resolution — `UserRoleRepository` (mock `UserRoles` table)

`role_repository.py`, following the existing repository naming/shape conventions ([crud_repository.py](src/pilot_api/repository/crud_repository.py)) but hard-coded, per the spec:

```python
_MOCK_USER_ROLES: dict[str, str] = {
    "reader_user": "read_only_role",
    "working_user": "read_write_role",
    "working_admin_user": "admin_role",
}

class UserRoleRepository:
    def get_role_for_user(self, user_id: str) -> str | None:
        return _MOCK_USER_ROLES.get(user_id)
```

**Design decision:** the token's own roles (`token_roles`) are captured for context/audit as required, but the actual RBAC *decision* is made against `effective_role`, resolved by looking up the token's `preferred_username` claim (falling back to `sub`) in `UserRoleRepository`. This is what the spec's "Users and roles" subsection under **Authorization** describes literally (a repository keyed by `UserId` returning one of the three role names), and it decouples the RBAC exercise from needing the realm's actual role configuration to line up with `read_only_role`/`read_write_role`/`admin_role`. Flagging this explicitly in case the intent was instead "trust `realm_access.roles` directly, and the mock repository is illustrative only" — easy to swap by changing one line in `SecurityHelper` if so.

### 6.3 Method → role matrix

```python
_ROLE_RANK = {"read_only_role": 1, "read_write_role": 2, "admin_role": 3}

_READ_METHODS  = {"GET", "HEAD", "OPTIONS", "QUERY", "TRACE"}
_WRITE_METHODS = {"PATCH", "POST", "PUT"}
_ADMIN_METHODS = {"DELETE"}

_METHOD_MIN_RANK = (
    {m: 1 for m in _READ_METHODS}
    | {m: 2 for m in _WRITE_METHODS}
    | {m: 3 for m in _ADMIN_METHODS}
)

def is_authorized(effective_role: str | None, method: str) -> bool:
    return _ROLE_RANK.get(effective_role, 0) >= _METHOD_MIN_RANK.get(method, 3)
```

Note: FastAPI/Starlette do not route `QUERY` or `TRACE` today — none of the current endpoints use them. They're included in the matrix for completeness/spec-fidelity but won't be exercised by any live route.

## 7. Active Flag Behavior

`security_active` (settings) controls what happens when authentication or authorization fails:

- **Active (`true`, default):** raise on failure → request is blocked.
  - No/invalid token → `UnauthorizedError` (401).
  - Valid token, insufficient role → `ForbiddenError` (403).
- **Inactive (`false`):** failure does **not** block the request. `SecurityHelper.enforce` instead:
  - Sets a `Warning` response header (RFC 7234 style: `Warning: 299 pilot-api "<reason>"`), and
  - Returns an anonymous `SecurityContext` so the endpoint still executes.

Because the dependency runs before the route handler but shares the same `Response` object, this only requires adding `response: Response` as a parameter to `SecurityHelper.enforce` — no extra middleware needed.

## 8. Centralization — `SecurityHelper`

`security_helper.py` is the single place new security logic lives, per the spec's **Centralization** requirement:

```python
class SecurityHelper:
    def __init__(self, settings: Settings, token_validator: TokenValidator, role_repository: UserRoleRepository):
        ...

    async def enforce(self, request: Request, response: Response) -> SecurityContext:
        """FastAPI dependency: authenticate, authorize, log, honor `security_active`."""

    def _authenticate(self, request: Request) -> SecurityContext: ...
    def _authorize(self, context: SecurityContext, method: str) -> None: ...  # raises ForbiddenError
    def _log_success(self, context: SecurityContext, request: Request) -> None: ...
    def _log_failure(self, reason: str, request: Request) -> None: ...

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
```

`get_security_helper()` mirrors the existing `get_settings()` singleton pattern and is what gets wired into the router as `Depends(get_security_helper().enforce)` (or, more testably, a thin module-level `async def enforce_security(...)` wrapper that resolves the helper via `Depends(get_security_helper)`).

## 9. Logging & Redaction

- On every authentication attempt, log at `INFO` (success) or `WARNING` (failure) via `logging.getLogger(__name__)`, consistent with the rest of the app.
- Per spec, extract the raw JWT from the `Authorization` header and include it in the log entry (both success and failure), alongside `user_id`, `effective_role`, `request.method`, `request.url.path`, and the existing `request_id`/`correlation_id` (already on `request.state` via `RequestContextMiddleware`).
- **Flagging a real risk here:** logging raw bearer tokens is sensitive-data exposure in any environment where log output isn't tightly access-controlled. Implementing it as specified since this is explicitly requested for this POC, but calling it out now as something to reconsider (truncate/hash the token, or gate it behind a debug-only setting) before this pattern is used against a non-throwaway realm.
- Add a `SensitiveDataFilter` logging filter in [logging_config.py](src/pilot_api/config/logging_config.py), registered alongside the existing `RequestContextFilter`, that redacts common password patterns (`password=...`, `pwd=...`, HTTP Basic `Authorization: Basic <b64>`) from any log record's message — this covers "passwords must be redacted, if present in any log entry" globally, not just on the security code path (e.g. it also protects against `db_password` ever leaking through an exception message).

## 10. Error Handling

Add to [exception/errors.py](src/pilot_api/exception/errors.py), following the existing `AppError` subclass pattern (already routed through `register_exception_handlers` → `ProblemDetailsDto`):

```python
class UnauthorizedError(AppError):
    status_code = 401
    title = "Unauthorized"

class ForbiddenError(AppError):
    status_code = 403
    title = "Forbidden"
```

No changes needed to `exception/handlers.py` — `AppError` is already handled generically.

## 11. Wiring Into Routes

In [api/routes/v1/__init__.py](src/pilot_api/api/routes/v1/__init__.py):

```python
from fastapi import APIRouter, Depends

from pilot_api.api.routes.v1.resources import router as resources_router
from pilot_api.security.security_helper import get_security_helper

API_VERSION = "1.0"

router = APIRouter(prefix=f"/v{API_VERSION.split('.')[0]}")
router.include_router(
    resources_router,
    dependencies=[Depends(lambda: get_security_helper())],  # resolved to .enforce, see below
)
```

(Exact shape TBD during implementation — likely a small `async def enforce_security(request: Request, response: Response, helper: SecurityHelper = Depends(get_security_helper)) -> SecurityContext` wrapper function in `security_helper.py`, used as `Depends(enforce_security)`, so FastAPI's dependency-injection/caching works cleanly and tests can override just `get_security_helper`.)

`system_router` (`/healthcheck`, `/about`) is included separately in [router.py](src/pilot_api/api/router.py) and is untouched — it remains open, satisfying the exclusion requirement structurally rather than via a bypass list.

Resource handlers that want the resolved `SecurityContext` (e.g. to include `user_id` in a future audit trail) can additionally take it as `Depends(enforce_security)` — FastAPI dependency caching means it won't re-run the check.

## 12. Testing Plan

New `tests/security/` package, mirroring `src/pilot_api/security/`:

| File | Covers |
| --- | --- |
| `tests/security/test_token_validator.py` | Valid token, expired token, bad signature, wrong issuer, wrong audience, malformed header — using a locally generated RSA keypair and a fake JWKS resolver (no network calls) |
| `tests/security/test_role_repository.py` | All three mock users resolve to their expected role; unknown user → `None` |
| `tests/security/test_authorization_matrix.py` | All 9 (role × method-tier) combinations, plus unknown/`None` role denied everywhere |
| `tests/security/test_security_helper.py` | `enforce()` under `security_active=True` (blocks on missing/invalid/insufficient) and `security_active=False` (allows + sets `Warning` header); success/failure logging fires with expected fields |
| `tests/security/test_redaction_filter.py` | Password-like patterns are scrubbed from formatted log output |

Extend existing integration coverage:

- `tests/api/routes/system/test_system.py` — add a regression assertion that `/healthcheck` and `/about` succeed with **no** `Authorization` header (proves the exclusion held).
- New `tests/api/routes/resources/test_security_enforcement.py` — end-to-end via the existing `client` fixture ([conftest.py](tests/conftest.py)), overriding `get_security_helper`/`get_session` the same way `get_session` is already overridden, to drive a couple of representative resource endpoints (e.g. `categories`, `order-details`) through: no token → 401; `reader_user` token → GET allowed, POST/DELETE denied; `working_user` token → GET/POST allowed, DELETE denied; `working_admin_user` token → all allowed; `security_active=False` → all allowed regardless, with `Warning` header present on the otherwise-failing cases.

All new and existing tests run via `python -m pytest` and must pass before this work is considered complete, per the spec's **Testing** requirement.

## 13. Documentation

Add a **Security** section to [README.md](README.md), after **Migrations** and before **Test**, covering:
- The new `.env` variables (`SECURITY_ACTIVE`, `IDENTITY_PROVIDER_*`) alongside the existing DB blocks.
- How `SECURITY_ACTIVE` changes behavior (block vs. warn-and-allow).
- A worked example: obtaining a token from the local dev IDP instance (`http://localhost:55001`, realm `local-realm`, client `local-client`) via the standard OAuth2 token endpoint, then calling a protected endpoint:

```bash
curl -X POST "http://localhost:55001/realms/local-realm/protocol/openid-connect/token" \
  -d "grant_type=password&client_id=local-client&username=working_user&password=<pwd>"

curl "http://localhost:53060/v1/categories/get-all" \
  -H "Authorization: Bearer <access_token>"
```

## 14. Out-of-Scope / Follow-ups

- The shared OpenAPI contract ([shared/SharedModule/OpenAPI/PilotApi_v1.yaml](shared/SharedModule/OpenAPI/PilotApi_v1.yaml)) currently declares no `securitySchemes`. It lives in a separate submodule repo (`PilotSharedSource`); updating it to document the new `bearerAuth` requirement is a natural follow-up but is out of scope here since it isn't owned by this repo.
- Real production hardening of the raw-JWT logging noted in §9.
- Wiring a real `UserRoles` table/database once one exists, replacing the hard-coded `UserRoleRepository` dict (the class boundary is deliberately drawn so this is a drop-in swap later).

## 15. Implementation Order

1. `pyproject.toml`: add `pyjwt[crypto]`.
2. `config/settings.py`: new settings + resolved URL properties. `.env.example` + README env blocks.
3. `exception/errors.py`: `UnauthorizedError`, `ForbiddenError`.
4. `security/context.py`, `security/role_repository.py`, `security/token_validator.py`.
5. `security/security_helper.py` + `get_security_helper()`.
6. `config/logging_config.py`: `SensitiveDataFilter`.
7. Wire `enforce_security` into `api/routes/v1/__init__.py`.
8. Tests (§12), run `python -m pytest` to green.
9. README **Security** section.

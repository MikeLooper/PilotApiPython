from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SecurityContext:
    """The enriched "context User": everything auth/authz code needs about the caller."""

    is_authenticated: bool
    user_id: str | None
    token_roles: frozenset[str]
    scopes: frozenset[str]
    client_attributes: dict[str, Any] = field(default_factory=dict)
    effective_role: str | None = None
    claims: dict[str, Any] = field(default_factory=dict)
    auth_failure_reason: str | None = None

    @classmethod
    def anonymous(cls, reason: str) -> "SecurityContext":
        return cls(
            is_authenticated=False,
            user_id=None,
            token_roles=frozenset(),
            scopes=frozenset(),
            auth_failure_reason=reason,
        )

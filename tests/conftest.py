import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["LOG_JSON"] = "false"

from pilot_api.api.dependencies import get_session
from pilot_api.main import app
from pilot_api.model.base import Base
from pilot_api.security.context import SecurityContext
from pilot_api.security.security_helper import enforce_security


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _override_enforce_security() -> SecurityContext:
    return SecurityContext(
        is_authenticated=True,
        user_id="working_admin_user",
        token_roles=frozenset({"admin_role"}),
        scopes=frozenset(),
        effective_role="admin_role",
    )


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    # Security enforcement is exercised by tests/security and
    # tests/api/routes/resources/test_security_enforcement.py; every other
    # test in the suite is about business logic and should not need a token.
    app.dependency_overrides[enforce_security] = _override_enforce_security
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

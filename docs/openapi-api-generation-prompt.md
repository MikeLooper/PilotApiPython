You are a senior Python architect. Generate a production-ready Python REST API project from an OpenAPI specification file.

Important constraints:
- Use the OpenAPI specification as the source of truth for API paths, operations, request and response schemas, error models, and validation rules.
- Do not invent or modify endpoints unless explicitly required by the OpenAPI file.
- Keep generated code and architecture aligned with modern Python best practices.
- Favor maintainability, testability, clear separation of concerns, and clean architecture principles.

Inputs you must use:
- OpenAPI spec location: ./shared/SharedModule/OpenAPI/PilotApi_v1.yaml
- Python version: latest stable 3.x
- Target database: SQL Server
- Auth strategy: None

Primary objective:
Create a complete Python API application structure whose endpoints and DTO contracts are defined by the OpenAPI spec, with robust internal layering and implementation best practices.

Technology baseline:
- Web framework: FastAPI
- Validation and schema modeling: Pydantic v2
- ORM and DB access: SQLAlchemy 2.0
- SQL Server driver: mssql+pyodbc (or equivalent SQLAlchemy-compatible driver)
- Migrations: Alembic
- Testing: pytest with httpx TestClient support
- Packaging and tooling: pyproject.toml

Architecture and structural requirements:
- Organize modules by bounded responsibility with explicit layers:
  - config
  - api (or controller)
  - dto
  - mapper
  - service
  - repository
  - model (entity and domain)
  - exception
  - validation
  - security (only if auth is required)
- Keep API layer thin: only HTTP concerns (status codes, routing, request parsing, response shaping, validation triggering).
- Implement business logic in service layer.
- Isolate persistence in repository layer.
- Keep mapping between domain models and DTOs in dedicated mappers.
- Use dependency injection consistently (FastAPI Depends and constructor injection for class-based services and repositories).
- Follow SOLID principles and avoid God classes.

OpenAPI-driven implementation requirements:
- Generate endpoint handlers that match operationIds and paths from the OpenAPI spec.
- Implement request and response DTOs exactly according to the spec schemas.
- Apply field and payload validation consistent with OpenAPI constraints.
- Implement consistent error responses that match spec-defined error models.
- Ensure content types, response codes, and required headers are respected.
- Preserve parameter styles and locations (path, query, header, cookie) exactly as defined.

Cross-cutting and quality requirements:
- Global exception handling with a standardized error envelope.
- Input validation with clear, client-friendly error messages.
- Logging strategy:
  - structured logs
  - no sensitive data in logs
  - meaningful contextual fields (request id, operation id, correlation id where available)
- Externalized configuration via environment variables and typed settings.
- Include health and readiness endpoints suitable for orchestration environments.
- Expose API docs aligned with OpenAPI source.
- Use pagination, sorting, and filtering patterns where endpoints indicate collection access.

Data and persistence requirements (if persistence is required):
- Use clear entity modeling and repository abstractions.
- Keep transaction boundaries in service layer.
- Use Alembic migrations for schema changes.
- Do not couple ORM entities directly to public API contracts unless explicitly justified.

Security requirements (if auth is required):
- Implement stateless authentication and authorization per input strategy.
- Enforce endpoint-level authorization rules.
- Validate and sanitize security-sensitive inputs.
- Use secure defaults (CORS configuration, security headers, CSRF strategy appropriate for stateless APIs).

Testing requirements:
- Unit tests for service logic.
- API tests for request and response behavior and validation.
- Integration tests for API and persistence slices where appropriate.
- Cover success, validation failures, not-found, conflict, and unexpected-error scenarios.

Non-functional requirements:
- Clear README with setup, run, test, migration, and environment configuration steps.
- Deterministic dependency resolution and runnable local profile.
- Idiomatic Python naming conventions and consistent formatting.
- No dead code, placeholders, or TODO stubs in core paths.

Generation process you must follow:
1. Parse and summarize the OpenAPI specification.
2. Produce the proposed package and module structure before code generation.
3. Map OpenAPI operations to API handlers and service methods.
4. Map schemas to DTOs and domain models, documenting transformation boundaries.
5. Define exception and error-response strategy.
6. Define repository contracts and transactional service flows.
7. Define test strategy per endpoint and critical business behavior.
8. Generate the project files accordingly.

Output format required from you:
- Start with a concise architecture summary.
- Then provide the full project tree.
- Then provide all generated files with complete content.
- Then provide run and test instructions.
- Then provide a brief checklist showing how implementation satisfies OpenAPI and architecture requirements.

Guardrails:
- Do not skip layers for convenience.
- Do not place business logic in API handlers.
- Do not diverge from OpenAPI contract.
- Do not output pseudo-code where concrete implementation is expected.
- If the OpenAPI spec and a requirement conflict, prioritize the OpenAPI contract and explicitly document the conflict and chosen resolution.
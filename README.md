# PilotApiPython

A proof of concept API to explore best-practices and new ideas (Python) - mainly executed via AI conversations.

## Generated Python API

This repository now includes a production-oriented FastAPI implementation generated from the OpenAPI contract in `shared/SharedModule/OpenAPI/PilotApi_v1.yaml`.

### Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- Alembic
- SQL Server driver via `mssql+pyodbc`
- pytest + FastAPI TestClient

### Project Structure

- `src/pilot_api/config`: typed settings, DB engine, logging setup
- `src/pilot_api/api`: route registration and HTTP handlers
- `src/pilot_api/dto`: OpenAPI-aligned request and response DTOs
- `src/pilot_api/mapper`: DTO <-> entity mapping
- `src/pilot_api/service`: business and transaction flows
- `src/pilot_api/repository`: persistence abstractions
- `src/pilot_api/model`: SQLAlchemy entities and domain objects
- `src/pilot_api/exception`: custom errors and global exception handlers
- `src/pilot_api/validation`: header and request validation helpers
- `src/pilot_api/security`: JWT authentication, role-based authorization, and the `SecurityHelper` that centralizes both
- `alembic`: migration configuration and initial schema
- `tests`: API and service-layer tests

### Northwind Coverage

The API now maps to the full set of classic Northwind tables:

- `Categories`
- `CustomerCustomerDemo`
- `CustomerDemographics`
- `Customers`
- `Employees`
- `EmployeeTerritories`
- `Order Details`
- `Orders`
- `Products`
- `Region`
- `Shippers`
- `Suppliers`
- `Territories`

To avoid unintended schema changes, the application does not execute automatic DDL on startup.

## Setup

1. Create and activate a Python environment.

2. Install dependencies:

```bash
python -m pip install -e .[dev]
```

3. Create your environment file:

```bash
copy .env.example .env
```

4. Update `.env` with database attributes:

- SQL Server

```bash
APP_NAME=PilotApiPython
APP_VERSION=1.0.0
LOG_LEVEL=INFO
LOG_JSON=true
DB_NAME=NorthWind
DB_CONNECT_TIMEOUT=30
DB_HOST=localhost
DB_PASSWORD=<DevUser password>
DB_PORT=1433
DB_SCHEMA=dbo
DB_USER=DevUser
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=true
# Optional full override:
# DATABASE_URL=mssql+pyodbc://DevUser:<DevUser password>@localhost:1433/NorthWind?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&timeout=30
SHOW_ABOUT_CONFIG=false
SECURITY_ACTIVE=true
IDENTITY_PROVIDER_BASE_URL=http://localhost:55001
IDENTITY_PROVIDER_REALM=local-realm
IDENTITY_PROVIDER_CLIENT_ID=local-client
IDENTITY_PROVIDER_AUDIENCE=
```

- PostgreSQL

```bash
APP_NAME=PilotApiPython
APP_VERSION=1.0.0
LOG_LEVEL=INFO
LOG_JSON=true
DB_BACKEND=postgresql
DB_NAME=northwind
DB_CONNECT_TIMEOUT=30
DB_HOST=localhost
DB_PASSWORD=<DevUser password>
DB_PORT=5432
DB_SCHEMA=pilot
DB_USER=DevUser
DB_TRUST_SERVER_CERTIFICATE=true
# Optional full override:
# DATABASE_URL=postgresql+psycopg://DevUser:<DevUser password>@localhost:5432/northwind?connect_timeout=30&options=-csearch_path%3Dpilot
SHOW_ABOUT_CONFIG=false
SECURITY_ACTIVE=true
IDENTITY_PROVIDER_BASE_URL=http://localhost:55001
IDENTITY_PROVIDER_REALM=local-realm
IDENTITY_PROVIDER_CLIENT_ID=local-client
IDENTITY_PROVIDER_AUDIENCE=
```

5. Environment Variable Overrides

Use `DB_HOST=local_mssql` only when the API process runs inside the same Docker network where that service name exists.

You can also set `DATABASE_URL` directly to override attribute-based construction.

The application listens on port `8000` by default, but this can be overrriden.

The database backend can also be switched with `DB_BACKEND`:

- `DB_BACKEND=sqlserver` uses the existing SQL Server connection settings.
- `DB_BACKEND=postgresql` uses the PostgreSQL connection profile with:
  - database name: `northwind`
  - host: `localhost`
  - port: `5432`
  - schema: `pilot`
  - user: `DevUser`

Example:

```bash
$env:DB_BACKEND = "postgresql"
```

## Run

Start the FastAPI application with your preferred ASGI server. For example, if you still have Uvicorn installed locally, you can run:

```bash
python -m uvicorn pilot_api.main:app --reload --app-dir src
```

If you are using a different ASGI host, launch the app through that runtime instead.

The above will use port 8000 by default.

If you would like to specify the host name and port, use the following:

```bash
python -m uvicorn pilot_api.main:app --reload --app-dir src --port 53060 --host localhost
```

API docs:

- Swagger UI: `http://localhost:53060/docs`
- ReDoc: `http://localhost:53060/redoc`

## Migrations

Create a migration:

```bash
python -m alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
python -m alembic upgrade head
```

## Security

All `/v1/...` domain endpoints require a bearer JWT, validated against a self-hosted OAuth2/OIDC identity provider (issuer + JWKS resolved from `IDENTITY_PROVIDER_*` settings). The System endpoints (`/healthcheck`, `/about`) are not protected.

Authorization is role-based. The token's subject is looked up in a mock `UserRoles` table to resolve one of three roles, each permitting a tier of HTTP methods:

| Role | Methods allowed |
| --- | --- |
| `read_only_role` | GET, HEAD, OPTIONS, QUERY, TRACE |
| `read_write_role` | the above, plus PATCH, POST, PUT |
| `admin_role` | the above, plus DELETE |

Mock users (for local testing): `reader_user`, `working_user`, `working_admin_user`.

`SECURITY_ACTIVE` controls what happens when authentication or authorization fails:

- `true` (default): the request is rejected (`401` if the token is missing/invalid, `403` if the role is insufficient).
- `false`: the request still proceeds, but the response carries a `Warning` header describing why authentication/authorization did not succeed.

Example: obtain a token from the local dev identity provider, then call a protected endpoint:

```bash
curl -X POST "http://localhost:55001/realms/local-realm/protocol/openid-connect/token" \
  -d "grant_type=password&client_id=local-client&username=working_user&password=<password>"

curl "http://localhost:53060/v1/categories/get-all" \
  -H "Authorization: Bearer <access_token>"
```

## Test

```bash
python -m pytest
```

The test suite uses an isolated in-memory SQLite database with dependency overrides for fast local verification.

## Shared SubModule

This repository includes the shared codebase as a Git submodule at:

- `shared/SharedModule`

Source:

- `https://github.com/MikeLooper/PilotSharedSource`

## Clone With SubModules

For a first-time clone, include submodules so `shared/SharedModule` is ready immediately:

```bash
git clone --recurse-submodules <this-repo-url>
```

If you already cloned without submodules, initialize and fetch them:

```bash
git submodule update --init --recursive
```

## Update The Shared SubModule

When changes are made in `PilotSharedSource`, pull the latest tracked branch for this submodule:

```bash
git submodule update --remote --merge shared/SharedModule
```

Then commit the updated submodule pointer in this repository:

```bash
git add shared/SharedModule .gitmodules
git commit -m "Update shared submodule"
```

## Development

### VS Code

To automatically run this application and launch the API UI, create a .vscode\launch.json file with the follwing contents:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Pilot API",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "pilot_api.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "53060"
            ],
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "serverReadyAction": {
                "action": "openExternally",
                "pattern": "Uvicorn running on http://\\S+:(\\d+)",
                "uriFormat": "http://localhost:%s/docs"
            },
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```


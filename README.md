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

4. Update `.env` with SQL Server attributes:

```bash
DB_NAME=NorthWind
DB_CONNECT_TIMEOUT=30
DB_HOST=localhost
DB_PASSWORD=<DevUser password>
DB_PORT=1433
DB_SCHEMA=dbo
DB_USER=DevUser
```

Use `DB_HOST=local_mssql` only when the API process runs inside the same Docker network where that service name exists.

You can also set `DATABASE_URL` directly to override attribute-based construction.

## Run

```bash
python -m uvicorn pilot_api.main:app --reload --app-dir src
```

API docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Migrations

Create a migration:

```bash
python -m alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
python -m alembic upgrade head
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

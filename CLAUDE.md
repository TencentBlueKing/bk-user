# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

bk-user (蓝鲸用户管理) is TencentBlueKing's enterprise user management and unified login solution. It provides multi-layer organizational structure management, data synchronization from various sources (LDAP, MAD, Excel), and authentication services.

## Repository Structure

```
src/
├── bk-user/     # User management backend (Django)
├── bk-login/    # Unified login service (Django)
├── idp-plugins/ # Identity provider plugins (shared between bk-user and bk-login)
└── pages/       # User management frontend
```

## Development Commands

### Initial Setup

```bash
# Install uv (package manager)
pip install uv

# Install pre-commit hooks (from repo root)
pip install pre-commit && pre-commit install

# Symlink IDP plugins (required)
ln -s $(pwd)/src/idp-plugins/idp_plugins $(pwd)/src/bk-login/bklogin
ln -s $(pwd)/src/idp-plugins/idp_plugins $(pwd)/src/bk-user/bkuser
```

### bk-user Service

```bash
cd src/bk-user

# Install dependencies
uv sync --dev

# Database migration
python manage.py migrate

# Run web server
python manage.py runserver user.example.com:8000
# Or: ./bin/start.sh

# Run tests
make test
# Or directly: pytest --maxfail=1 -l --reuse-db tests --disable-warnings -vv

# Run a single test file
pytest tests/apis/web/test_xxx.py -vv

# Run a specific test
pytest tests/apis/web/test_xxx.py::test_function_name -vv

# Check code layers
lint-imports
```

### bk-login Service

```bash
cd src/bk-login

# Install dependencies
uv sync --dev

# Database migration
python manage.py migrate

# Run web server
python manage.py runserver login.example.com:8000
# Or: ./bin/start.sh

# Run tests
make test
```

### Code Quality (Pre-commit)

Pre-commit runs automatically. Manual execution:
- `ruff format --config=src/bk-user/pyproject.toml src/bk-user/` - Format code
- `ruff check --config=src/bk-user/pyproject.toml --fix src/bk-user/` - Lint code
- `mypy --config-file=src/bk-user/pyproject.toml src/bk-user/` - Type check

## Architecture

### Layered Architecture (bk-user)

The codebase enforces strict layered architecture via import-linter:

```
apis / auth / monitoring  (Top layer - API endpoints)
    ↓
biz                       (Business logic)
    ↓
apps                      (Django apps - models, sync logic)
    ↓
plugins                   (Data source plugins)
    ↓
component                 (External service clients)
    ↓
common                    (Shared utilities)
    ↓
utils                     (Basic utilities)
```

**Key constraint**: Higher layers can import from lower layers, but not vice versa.

### Django Apps (bk-user)

- `apps/data_source/` - Data source management (LDAP, local, MAD)
- `apps/tenant/` - Multi-tenant management, collaboration strategies
- `apps/sync/` - Data synchronization (runners, syncers, tasks)
- `apps/idp/` - Identity provider configuration
- `apps/notification/` - Email/SMS notifications
- `apps/permission/` - Permission management

### API Modules (bk-user)

- `apis/web/` - Frontend-facing APIs (organization, data_source, tenant_setting, etc.)
- `apis/login/` - Login service APIs
- `apis/open_v1/`, `open_v2/`, `open_v3/` - External APIs (versioned)
- `apis/apigw/` - API Gateway integrations

### Plugin Systems

**Data Source Plugins** (`bkuser/plugins/`):
- `local/` - Local data source (Excel import)
- `ldap/` - LDAP/Active Directory
- `general/` - HTTP-based custom sources

Custom plugins must use `custom_` prefix for ID.

**IDP Plugins** (`src/idp-plugins/idp_plugins/`):
- Credential-based: local, ldap, mad
- Federation-based: wecom, oauth2.0, oidc, saml2.0

Custom IDP plugins must also use `custom_` prefix.

### Key Models

**DataSource** (`apps/data_source/models.py`):
- Unique constraint: `(owner_tenant_id, type)` - one data source per type per tenant
- Supports local, LDAP, MAD, and custom plugins

**TenantUser** (`apps/tenant/models.py`):
- Primary key `id` can be nanoid, uuid, or legacy `username@domain` format
- Links to `DataSourceUser` and `Tenant`

**CollaborationStrategy** (`apps/tenant/models.py`):
- Enables cross-tenant user sharing between source and target tenants

### Sync Architecture (`apps/sync/`)

Layered sync system:
```
periodic_tasks  (Celery beat schedules)
    ↓
managers        (Sync orchestration)
    ↓
tasks           (Celery tasks)
    ↓
runners         (DataSourceSyncRunner, TenantSyncRunner)
    ↓
syncers         (DataSourceUserSyncer, TenantUserSyncer)
    ↓
models          (SyncTask, SyncLog)
```

## Configuration

Both services use `.env` files for configuration. Key variables:
- Database: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_NAME`
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- App secrets: `BK_APP_CODE`, `BK_APP_SECRET`, `BKKRILL_ENCRYPT_SECRET_KEY`

See `bkuser/settings.py` and `bklogin/settings.py` for all options.

## Testing

Tests are in `src/bk-user/tests/` with structure mirroring `bkuser/`:
- `tests/apis/` - API endpoint tests
- `tests/apps/` - Django app tests
- `tests/biz/` - Business logic tests
- `tests/plugins/` - Plugin tests

Use `--reuse-db` flag to speed up test runs by reusing the test database.

# FastAPI + SQLite backend with +TKinter frontend MVP Development Plan

## MVP Developmen approach - Test Driven Development (TDD)

### Core TDD Principle: Tests Must Import Like End Users

In TDD, you write tests first, which means:
1. **Tests define the public API** before implementation exists
2. **Import statements in tests** must match how users will import your code
3. **Test failures should reflect real usage problems**, not development artifacts

**Benefits:**
- Tests import exactly like end users
- Consistent behavior in dev, CI, and production
- No `sys.path` hacks needed
- Package installation doesn't break tests

## TDD Workflow Example

### Basic workflow

Install in development mode (editable)
`uv pip install -e .`

Run tests (imports work correctly)
`uv run pytest`

Run specific test
`uv run pytest tests/test_models/test_work_item.py -v`

Run with coverage
`uv run pytest --cov=dbr --cov-report=html`

Start development server
`uv run uvicorn dbr.main:app --reload`


### Red-Green-Refactor with Src Layout

**Step 1: Red (Test First)**
```python
# tests/test_dbr_engine.py
from dbr.services.dbr_engine import DBREngine  # Module doesn't exist yet!

def test_advance_time_unit():
    engine = DBREngine()
    result = engine.advance_time_unit("ORG-123")
    assert result["advanced_schedules_count"] >= 0
```

**Step 2: Green (Minimal Implementation)**
```python
# src/dbr/services/dbr_engine.py
class DBREngine:
    def advance_time_unit(self, org_id: str) -> dict:
        return {"advanced_schedules_count": 0}
```

**Step 3: Refactor (Improve Implementation)**
```python
# src/dbr/services/dbr_engine.py
from ..models.schedule import Schedule

class DBREngine:
    def advance_time_unit(self, org_id: str) -> dict:
        # Real implementation
        schedules = Schedule.get_active_for_org(org_id)
        count = len(schedules)
        # ... actual logic
        return {"advanced_schedules_count": count}
```


## MVP 1: FastAPI Backend with SQLite (1-2 weeks)

### Technology Stack
- **FastAPI** - Modern Python API framework
- **SQLAlchemy** - ORM with SQLite database
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization
- **SQLite** - File-based database (zero setup)
- **Pytest + httpx** - API testing

### Project Structure
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # Settings and configuration
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── deps.py          # Dependency injection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── work_item.py
│   │   ├── schedule.py
│   │   └── ccr.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── work_item.py
│   │   ├── schedule.py
│   │   └── common.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── deps.py          # Route dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── organizations.py
│   │       ├── work_items.py
│   │       ├── schedules.py
│   │       ├── ccrs.py
│   │       └── system.py
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── dbr_engine.py    # Core DBR mechanics
│       ├── planning.py      # Planning logic
│       └── time_progression.py
├── alembic/                 # Database migrations
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
├── data/
│   └── dbr.db              # SQLite database
├── requirements.txt
├── .env
└── README.md
```

### Key Benefits of This Approach
1. **API-First Design**: Validates your OpenAPI specification
2. **Easy Migration Path**: Change database URL when ready for PostgreSQL
3. **Automatic Documentation**: FastAPI generates interactive docs
4. **Type Safety**: Full type checking with Pydantic
5. **Testing**: Comprehensive API testing with pytest
6. **Rapid Development**: SQLite means no database setup

## MVP 2: Tkinter Frontend (1-2 weeks)

### Technology Stack
- **Tkinter** - Python's built-in GUI framework
- **requests** - HTTP client for API calls
- **threading** - For non-blocking API calls
- **json** - API data handling

### Frontend Structure
```
frontend/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── api_client.py        # FastAPI client wrapper
│   ├── models.py            # Data models matching API
│   ├── widgets/             # Custom Tkinter widgets
│   │   ├── __init__.py
│   │   ├── buffer_board.py  # Main buffer board
│   │   ├── work_item_list.py
│   │   ├── schedule_builder.py
│   │   └── ccr_status.py
│   ├── views/               # Main application views
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── planning_view.py
│   │   └── work_item_detail.py
│   └── utils/
│       ├── __init__.py
│       ├── formatting.py
│       └── validation.py
├── config.py
└── requirements.txt
```

### Integration Benefits
- **API Validation**: Frontend tests all API endpoints
- **Real-time Testing**: Tkinter app provides immediate feedback
- **Business Logic**: All logic in FastAPI, frontend is just visualization
- **Multi-user Ready**: Multiple Tkinter instances can hit same API
- **Documentation**: FastAPI docs help frontend development

## Development Phases

### Foundation First

- Authentication system with test users for each role
- Time management system using freezegun for testing
- Default organization setup for MVP simplicity

### Core DBR Logic

- Work items, schedules, CCRs with full business logic
- Time progression engine with buffer zone management
- Complete API layer with role-based access control

### Frontend Validation

- API client layer for backend integration
- Work item and schedule management UIs
- Planning interface for schedule creation

### Buffer Board

- Visual DBR board with time progression
- Standup meeting workflow
- Real-time buffer zone status

### Integration & Polish

- End-to-end testing of complete workflows
- Error handling and edge cases
- Performance optimization and UX polish
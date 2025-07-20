# TDD with Python

## Core TDD Principle: Tests Must Import Like End Users

In TDD, you write tests first, which means:
1. **Tests define the public API** before implementation exists
2. **Import statements in tests** must match how users will import your code
3. **Test failures should reflect real usage problems**, not development artifacts

## TDD with Src Layout for directories

**Example Src Layout Structure:**
```
dbr_backend/
├── src/
│   └── dbr/
│       ├── __init__.py
│       └── models/
│           └── work_item.py
├── tests/
│   └── test_work_item.py
├── pyproject.toml
└── README.md
```

**Test File:**
```python
# tests/test_work_item.py

# ✅ This is exactly how end users will import
from dbr.models.work_item import WorkItem

def test_work_item_creation():
    wi = WorkItem(title="Test", hours=8.0)
    assert wi.title == "Test"
```

**Benefits:**
- Tests import exactly like end users
- Consistent behavior in dev, CI, and production
- No `sys.path` hacks needed
- Package installation doesn't break tests

## TDD Workflow Examples


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

### API Testing with TDD

**Test-First API Development:**
```python
# tests/test_api/test_work_items.py
from fastapi.testclient import TestClient
from dbr.main import app  # Clean import!

client = TestClient(app)

def test_create_work_item():
    response = client.post("/api/v1/workitems", json={
        "organization_id": "ORG-123",
        "title": "Test Work Item",
        "estimated_total_hours": 8.0
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Work Item"
```

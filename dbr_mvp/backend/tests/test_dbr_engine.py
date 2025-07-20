# tests/test_dbr_engine.py
from dbr.services.dbr_engine import DBREngine  # Module doesn't exist yet!


def test_advance_time_unit():
    engine = DBREngine()
    result = engine.advance_time_unit("ORG-123")
    assert result["advanced_schedules_count"] >= 0
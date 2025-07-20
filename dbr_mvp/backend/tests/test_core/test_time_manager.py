# tests/test_core/test_time_manager.py
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
import pytz


def test_set_system_time():
    """Test manual time setting capability"""
    from dbr.core.time_manager import TimeManager
    
    # Test: Can set system time for testing
    test_time = datetime(2024, 1, 15, 10, 30, 0)
    time_manager = TimeManager()
    time_manager.set_current_time(test_time)
    
    # Test: Time persists across requests
    current_time = time_manager.get_current_time()
    assert current_time == test_time
    
    # Test: Can advance time manually
    time_manager.advance_time(hours=2)
    advanced_time = time_manager.get_current_time()
    expected_time = test_time + timedelta(hours=2)
    assert advanced_time == expected_time


def test_time_progression():
    """Test time advancement mechanics"""
    from dbr.core.time_manager import TimeManager
    
    time_manager = TimeManager()
    start_time = datetime(2024, 1, 15, 9, 0, 0)
    time_manager.set_current_time(start_time)
    
    # Test: Advance by hours/days/weeks
    time_manager.advance_time(hours=8)
    assert time_manager.get_current_time() == start_time + timedelta(hours=8)
    
    time_manager.advance_time(days=1)
    assert time_manager.get_current_time() == start_time + timedelta(hours=8, days=1)
    
    time_manager.advance_time(weeks=1)
    assert time_manager.get_current_time() == start_time + timedelta(hours=8, days=1, weeks=1)


def test_time_zones_handled_correctly():
    """Test time zone handling"""
    from dbr.core.time_manager import TimeManager
    
    time_manager = TimeManager()
    
    # Test: UTC time handling
    utc_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=pytz.UTC)
    time_manager.set_current_time(utc_time)
    assert time_manager.get_current_time() == utc_time
    
    # Test: Timezone conversion utilities exist
    assert hasattr(time_manager, 'to_timezone')
    
    # Test: Can convert to different timezone
    est_time = time_manager.to_timezone(utc_time, 'US/Eastern')
    assert est_time.tzinfo.zone == 'US/Eastern'


def test_time_manager_singleton():
    """Test that TimeManager maintains consistent state"""
    from dbr.core.time_manager import TimeManager
    
    # Test: Multiple instances share the same time state
    tm1 = TimeManager()
    tm2 = TimeManager()
    
    test_time = datetime(2024, 1, 15, 12, 0, 0)
    tm1.set_current_time(test_time)
    
    # Both instances should return the same time
    assert tm1.get_current_time() == tm2.get_current_time()


def test_freezegun_integration():
    """Test integration with freezegun for testing"""
    from dbr.core.time_manager import TimeManager
    
    # Test: Works with freezegun decorator
    with freeze_time("2024-01-15 10:00:00"):
        time_manager = TimeManager()
        # Should be able to get frozen time
        current = time_manager.get_current_time()
        assert current.year == 2024
        assert current.month == 1
        assert current.day == 15
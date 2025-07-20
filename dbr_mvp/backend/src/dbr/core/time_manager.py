# src/dbr/core/time_manager.py
from datetime import datetime, timedelta, timezone
from typing import Optional
import pytz
from freezegun import freeze_time


class TimeManager:
    """
    Manages system time for testing and development.
    Provides manual time control for DBR time progression.
    """
    
    _instance = None
    _current_time: Optional[datetime] = None
    
    def __new__(cls):
        """Singleton pattern to ensure consistent time state"""
        if cls._instance is None:
            cls._instance = super(TimeManager, cls).__new__(cls)
        return cls._instance
    
    def set_current_time(self, time: datetime) -> None:
        """Set the current system time for testing"""
        self._current_time = time
    
    def get_current_time(self) -> datetime:
        """Get the current system time"""
        if self._current_time is None:
            return datetime.now(timezone.utc)
        return self._current_time
    
    def advance_time(self, hours: int = 0, days: int = 0, weeks: int = 0, **kwargs) -> None:
        """Advance time by specified amount"""
        if self._current_time is None:
            self._current_time = datetime.now(timezone.utc)
        
        delta = timedelta(hours=hours, days=days, weeks=weeks, **kwargs)
        self._current_time += delta
    
    def to_timezone(self, dt: datetime, timezone_name: str) -> datetime:
        """Convert datetime to specified timezone"""
        target_tz = pytz.timezone(timezone_name)
        
        # If datetime is naive, assume UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        
        return dt.astimezone(target_tz)
    
    def reset(self) -> None:
        """Reset time manager state (useful for testing)"""
        self._current_time = None
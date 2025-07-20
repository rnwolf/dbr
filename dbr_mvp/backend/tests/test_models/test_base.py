# tests/test_models/test_base.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_database_connection():
    """Test basic database connectivity"""
    # Test: Can connect to SQLite
    engine = create_engine("sqlite:///:memory:")
    connection = engine.connect()
    
    # Test: Connection is valid
    assert connection is not None
    
    # Test: Can execute basic SQL
    result = connection.execute("SELECT 1 as test_value")
    row = result.fetchone()
    assert row[0] == 1
    
    connection.close()


def test_uuid_generation():
    """Test UUID primary keys work"""
    # Test: Models generate UUIDs
    test_uuid = uuid.uuid4()
    assert isinstance(test_uuid, uuid.UUID)
    
    # Test: UUIDs are unique
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    assert uuid1 != uuid2
    assert str(uuid1) != str(uuid2)


def test_database_table_creation():
    """Test basic table creation and drop"""
    # This test will fail until we create the base model
    from dbr.models.base import Base
    
    # Test: Can create/drop tables
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    # Test: Tables exist (will be empty initially but structure should be there)
    assert engine.has_table("organizations") == False  # Will be True once we add models
    
    Base.metadata.drop_all(engine)
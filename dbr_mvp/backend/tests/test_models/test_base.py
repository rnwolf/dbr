# tests/test_models/test_base.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid


def test_database_connection():
    """Test basic database connectivity"""
    # Test: Can connect to SQLite
    engine = create_engine("sqlite:///:memory:")
    
    # Use context manager to ensure proper cleanup
    with engine.connect() as connection:
        # Test: Connection is valid
        assert connection is not None
        
        # Test: Can execute basic SQL (using text() for SQLAlchemy 2.0)
        result = connection.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row[0] == 1
    
    # Properly dispose of the engine
    engine.dispose()


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
    # Test: Can import base model
    from dbr.models.base import Base, BaseModel
    
    # Test: Can create/drop tables
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        
        # Test: Base metadata exists
        assert Base.metadata is not None
        
        # Test: BaseModel has expected attributes
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'created_date')
        assert hasattr(BaseModel, 'updated_date')
        
        Base.metadata.drop_all(engine)
    finally:
        # Properly dispose of the engine
        engine.dispose()
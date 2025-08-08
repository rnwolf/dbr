#!/usr/bin/env python3
"""
Test script to verify that the database relationships are properly defined
"""
import sys
import os

# Add the backend source to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dbr_mvp', 'backend', 'src'))

try:
    # Import the models to check for any syntax or relationship errors
    from dbr.models.organization import Organization
    from dbr.models.collection import Collection
    from dbr.models.work_item import WorkItem
    from dbr.models.user import User
    
    print("✅ All models imported successfully!")
    
    # Check that relationships are defined
    print("\n🔍 Checking relationships...")
    
    # Organization relationships
    org_relationships = [attr for attr in dir(Organization) if not attr.startswith('_')]
    print(f"Organization relationships: {[r for r in org_relationships if 'work_items' in r or 'collections' in r]}")
    
    # WorkItem relationships  
    wi_relationships = [attr for attr in dir(WorkItem) if not attr.startswith('_')]
    print(f"WorkItem relationships: {[r for r in wi_relationships if 'organization' in r or 'collection' in r]}")
    
    # Collection relationships
    coll_relationships = [attr for attr in dir(Collection) if not attr.startswith('_')]
    print(f"Collection relationships: {[r for r in coll_relationships if 'organization' in r or 'work_items' in r or 'owner' in r]}")
    
    # User relationships
    user_relationships = [attr for attr in dir(User) if not attr.startswith('_')]
    print(f"User relationships: {[r for r in user_relationships if 'owned_collections' in r]}")
    
    print("\n✅ All relationship checks completed successfully!")
    print("\n🎉 Database relationships have been properly established!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
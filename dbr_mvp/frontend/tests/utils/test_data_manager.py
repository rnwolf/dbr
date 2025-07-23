# tests/utils/test_data_manager.py
"""Test data management utilities"""

class DataManager:
    """Manages test data for frontend integration tests"""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.created_items = []
    
    def create_test_organization(self, name="Test Org Frontend"):
        """Create test organization and track for cleanup"""
        if not self.api_client:
            raise ValueError("API client not set")
            
        org = self.api_client.create_organization({
            "name": name,
            "description": "Test organization for frontend testing",
            "contact_email": "frontend-test@example.com",
            "country": "US"
        })
        self.created_items.append(("organization", org["id"]))
        return org
    
    def create_test_work_item(self, org_id, title="Test Work Item Frontend"):
        """Create test work item and track for cleanup"""
        if not self.api_client:
            raise ValueError("API client not set")
            
        work_item = self.api_client.create_work_item({
            "organization_id": org_id,
            "title": title,
            "description": "Test work item for frontend testing",
            "estimated_total_hours": 8.0,
            "status": "Ready",
            "priority": "medium"
        })
        self.created_items.append(("work_item", work_item["id"]))
        return work_item
    
    def create_test_schedule(self, org_id, board_config_id, work_item_ids):
        """Create test schedule and track for cleanup"""
        if not self.api_client:
            raise ValueError("API client not set")
            
        schedule = self.api_client.create_schedule({
            "organization_id": org_id,
            "board_config_id": board_config_id,
            "work_item_ids": work_item_ids
        })
        self.created_items.append(("schedule", schedule["id"]))
        return schedule
    
    def cleanup(self):
        """Clean up all created test data"""
        if not self.api_client:
            return
            
        for item_type, item_id in reversed(self.created_items):
            try:
                if item_type == "organization":
                    self.api_client.delete_organization(item_id)
                elif item_type == "work_item":
                    self.api_client.delete_work_item(item_id)
                elif item_type == "schedule":
                    self.api_client.delete_schedule(item_id)
            except Exception as e:
                print(f"Warning: Could not cleanup {item_type} {item_id}: {e}")
        
        self.created_items.clear()
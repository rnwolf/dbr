# DBR SDK Methods Overview

## 📋 **Complete API Reference for DBR Python SDK**

This document provides a comprehensive overview of all available methods in the DBR (Drum Buffer Rope) Python SDK, organized by functional area.

---

## 🔧 **Authentication** (`sdk.authentication`)

### Methods
- `login(username, password)` → `LoginResponse`
- `get_current_user_info()` → `DbrAPIAuthUserInfo`
- `logout()` → `Any`

### Usage Examples
```python
# Login and get token
response = sdk.authentication.login(username="admin", password="admin123")
token = response.access_token

# Get current user information
user_info = sdk.authentication.get_current_user_info()
print(f"User: {user_info.username}, Email: {user_info.email}")

# Logout
sdk.authentication.logout()
```

### Key Fields
- **LoginResponse**: `access_token`, `user`, `token_type`
- **DbrAPIAuthUserInfo**: `id`, `username`, `email`, `display_name`, `active_status`

---

## 🏢 **Organizations** (`sdk.organizations`)

### Methods
- `get(status=None)` → `List[OrganizationResponse]`
- `create(name, contact_email, country, description=None, subscription_level="basic")` → `OrganizationResponse`
- `get_by_id(org_id)` → `OrganizationResponse`
- `update(org_id, name=None, description=None, contact_email=None, country=None, subscription_level=None, status=None)` → `OrganizationResponse`
- `delete(org_id)` → `Any`

### Usage Examples
```python
# Get all organizations
orgs = sdk.organizations.get()

# Create new organization (Super Admin only)
new_org = sdk.organizations.create(
    name="New Company",
    contact_email="admin@newcompany.com",
    country="US",
    description="A new organization"
)

# Update organization
updated_org = sdk.organizations.update(
    org_id=org.id,
    name="Updated Company Name",
    status="active"
)
```

### Key Fields
- **OrganizationResponse**: `id`, `name`, `description`, `status`, `contact_email`, `country`, `subscription_level`, `created_date`

---

## 👥 **Users** (`sdk.users`)

### Methods
- `get(organization_id)` → `List[UserResponse]`
- `create(organization_id, username, email, display_name, password, system_role_id, active_status=True)` → `UserResponse`
- `get_by_id(user_id)` → `UserResponse`
- `update(user_id, username=None, email=None, display_name=None, system_role_id=None, active_status=None)` → `UserResponse`
- `delete(user_id)` → `Any`

### Usage Examples
```python
# Get users in organization
users = sdk.users.get(organization_id=org_id)

# Create new user
new_user = sdk.users.create(
    organization_id=org_id,
    username="newuser",
    email="newuser@example.com",
    display_name="New User",
    password="secure_password",
    system_role_id=planner_role_id
)

# Update user role
updated_user = sdk.users.update(
    user_id=user.id,
    system_role_id=admin_role_id,
    active_status=True
)
```

### Key Fields
- **UserResponse**: `id`, `username`, `email`, `display_name`, `active_status`, `system_role_id`, `organization_id`

---

## 📦 **Collections** (`sdk.collections`)

### Methods
- `list(organization_id, type=None, status=None, owner_user_id=None, sort=None)` → `List[CollectionResponse]`
- `create(organization_id, name, description, type, status="planning", owner_user_id=None, target_completion_date=None, target_completion_date_timezone="UTC", estimated_sales_price=None, estimated_variable_cost=None, url=None)` → `CollectionResponse`
- `get(collection_id)` → `CollectionResponse`
- `update(collection_id, name=None, description=None, type=None, status=None, owner_user_id=None, target_completion_date=None, target_completion_date_timezone=None, estimated_sales_price=None, estimated_variable_cost=None, url=None)` → `CollectionResponse`
- `delete(collection_id)` → `Any`

### Usage Examples
```python
# List collections in organization
collections = sdk.collections.list(organization_id=org_id)

# Filter collections by type
projects = sdk.collections.list(organization_id=org_id, type="Project")

# Create new collection
new_collection = sdk.collections.create(
    organization_id=org_id,
    name="Q4 Product Release",
    description="Major product release for Q4",
    type="Release",
    status="planning",
    estimated_sales_price=100000.0,
    estimated_variable_cost=25000.0,
    target_completion_date="2024-12-31T23:59:59Z"
)

# Update collection status
updated_collection = sdk.collections.update(
    collection_id=collection.id,
    status="active"
)
```

### Key Fields
- **CollectionResponse**: `id`, `organization_id`, `name`, `description`, `type`, `status`, `owner_user_id`, `target_completion_date`, `estimated_sales_price`, `estimated_variable_cost`, `url`

### Collection Statuses
- `planning` - Initial planning phase
- `active` - Currently in progress
- `on-hold` - Temporarily paused
- `completed` - Finished

---

## 📋 **Work Items** (`sdk.work_items`)

### Methods
- `list(organization_id, collection_id=None, status=None, priority=None, sort=None, responsible_user_id=None)` → `List[WorkItemResponse]`
- `create(organization_id, title, description, collection_id=None, due_date=None, status="Backlog", priority="medium", estimated_total_hours=None, ccr_hours_required=None, estimated_sales_price=None, estimated_variable_cost=None, responsible_user_id=None, url=None)` → `WorkItemResponse`
- `get(work_item_id)` → `WorkItemResponse`
- `update(work_item_id, title=None, description=None, collection_id=None, due_date=None, status=None, priority=None, estimated_total_hours=None, ccr_hours_required=None, estimated_sales_price=None, estimated_variable_cost=None, responsible_user_id=None, url=None)` → `WorkItemResponse`
- `delete(work_item_id)` → `Any`
- `update_task(work_item_id, task_id, title=None, description=None, status=None, estimated_hours=None, actual_hours=None, responsible_user_id=None)` → `TaskResponse`

### Usage Examples
```python
# List work items in organization
work_items = sdk.work_items.list(organization_id=org_id)

# Filter by status and priority
ready_items = sdk.work_items.list(
    organization_id=org_id,
    status=["Ready", "In-Progress"],
    priority="high"
)

# Create new work item
new_item = sdk.work_items.create(
    organization_id=org_id,
    title="Implement user authentication",
    description="Add JWT-based authentication system",
    collection_id=collection.id,
    priority="high",
    estimated_total_hours=16.0,
    ccr_hours_required={"development": 12.0, "testing": 4.0}
)

# Update work item status
updated_item = sdk.work_items.update(
    work_item_id=item.id,
    status="In-Progress"
)
```

### Key Fields
- **WorkItemResponse**: `id`, `organization_id`, `collection_id`, `title`, `description`, `status`, `priority`, `estimated_total_hours`, `ccr_hours_required`, `tasks`

### Work Item Statuses
- `Backlog` - Not yet ready for work
- `Ready` - Ready to be scheduled
- `Standby` - Waiting for dependencies
- `In-Progress` - Currently being worked on
- `Done` - Completed

### Work Item Priorities
- `low` - Low priority
- `medium` - Normal priority
- `high` - High priority
- `critical` - Critical/urgent priority

---

## 📅 **Schedules** (`sdk.schedules`)

### Methods
- `list(organization_id, board_config_id=None, status=None, sort=None)` → `List[ScheduleResponse]`
- `create(organization_id, board_config_id, work_item_ids, capability_channel_id=None, status="Planning")` → `ScheduleResponse`
- `get(schedule_id)` → `ScheduleResponse`
- `update(schedule_id, work_item_ids=None, capability_channel_id=None, status=None, time_unit_position=None)` → `ScheduleResponse`
- `delete(schedule_id)` → `Any`
- `get_board_analytics(board_config_id)` → `BoardAnalytics`

### Usage Examples
```python
# List schedules for organization
schedules = sdk.schedules.list(organization_id=org_id)

# Create new schedule
new_schedule = sdk.schedules.create(
    organization_id=org_id,
    board_config_id=board.id,
    work_item_ids=[item1.id, item2.id],
    capability_channel_id="development"
)

# Get board analytics
analytics = sdk.schedules.get_board_analytics(board_config_id=board.id)
```

### Key Fields
- **ScheduleResponse**: `id`, `organization_id`, `board_config_id`, `work_item_ids`, `status`, `time_unit_position`, `total_ccr_hours`

### Schedule Statuses
- `Planning` - Being planned/created
- `Pre-Constraint` - Before the CCR
- `Post-Constraint` - After the CCR
- `Completed` - Finished

---

## ⚙️ **System** (`sdk.system`)

### Methods
- `advance_time_unit(organization_id, board_config_id=None)` → `AdvanceTimeResponse`
- `get_time()` → `Dict[str, Any]`
- `set_time(time_iso)` → `Dict[str, Any]`

### Usage Examples
```python
# Advance time by one unit (core DBR operation)
result = sdk.system.advance_time_unit(organization_id=org_id)
print(f"Processed {result.schedules_processed} schedules")

# Get current system time
current_time = sdk.system.get_time()

# Set system time (for testing)
sdk.system.set_time(time_iso="2024-01-01T00:00:00Z")
```

### Key Fields
- **AdvanceTimeResponse**: `schedules_processed`, `time_advanced_to`, `affected_schedules`

---

## 👥 **Memberships** (`sdk.memberships`)

### Methods
- `get(org_id, role_id=None, invitation_status=None)` → `List[MembershipResponse]`
- `create(org_id, user_id, role_id, invitation_status="pending")` → `MembershipResponse`
- `get_membership(org_id, user_id)` → `MembershipResponse`
- `update_membership(org_id, user_id, role_id=None, invitation_status=None)` → `MembershipResponse`
- `delete(org_id, user_id)` → `Any`

### Usage Examples
```python
# Get all memberships for organization
memberships = sdk.memberships.get(org_id=org_id)

# Create new membership
new_membership = sdk.memberships.create(
    org_id=org_id,
    user_id=user.id,
    role_id=planner_role_id,
    invitation_status="accepted"
)

# Update user's role in organization
updated_membership = sdk.memberships.update_membership(
    org_id=org_id,
    user_id=user.id,
    role_id=admin_role_id
)
```

### Key Fields
- **MembershipResponse**: `id`, `organization_id`, `user_id`, `role_id`, `invitation_status`, `joined_date`

---

## 🏥 **Health** (`sdk.health`)

### Methods
- `get()` → `Any`

### Usage Examples
```python
# Check service health
health = sdk.health.get()
print(f"Status: {health['status']}, Service: {health['service']}")
```

---

## 🔑 **Authentication & Authorization**

### Role-Based Access Control

#### **Super Admin**
- Full system access
- Can manage all organizations
- Can create/delete organizations
- Can manage global settings

#### **Organization Admin**
- Can manage their organization
- Can invite/manage users within organization
- Can create/update/delete collections
- Can configure organization settings

#### **Planner**
- Can create/update/delete work items and collections
- Can create and manage schedules
- Can advance time units
- Can view reports and analytics

#### **Worker**
- Can update assigned work items
- Can view work items and collections
- Can mark tasks as complete
- Limited to execution activities

#### **Viewer**
- Read-only access to all content
- Can view reports and dashboards
- Cannot modify any data

### Common Usage Patterns

#### **Initialize SDK with Authentication**
```python
from dbrsdk import Dbrsdk

# Initialize with token
sdk = Dbrsdk(
    server_url="http://localhost:8000",
    http_bearer="your_jwt_token"
)

# Or authenticate first
sdk = Dbrsdk(server_url="http://localhost:8000")
response = sdk.authentication.login(username="admin", password="admin123")
authenticated_sdk = Dbrsdk(
    server_url="http://localhost:8000",
    http_bearer=response.access_token
)
```

#### **Complete Workflow Example**
```python
# 1. Authenticate
response = sdk.authentication.login(username="planner", password="planner123")
auth_sdk = Dbrsdk(server_url=base_url, http_bearer=response.access_token)

# 2. Get organization
orgs = auth_sdk.organizations.get()
org_id = orgs[0].id

# 3. Create collection
collection = auth_sdk.collections.create(
    organization_id=org_id,
    name="Sprint 1",
    description="First development sprint",
    type="Project"
)

# 4. Create work items
work_item = auth_sdk.work_items.create(
    organization_id=org_id,
    collection_id=collection.id,
    title="User Login Feature",
    description="Implement user authentication",
    priority="high"
)

# 5. Create schedule
schedule = auth_sdk.schedules.create(
    organization_id=org_id,
    board_config_id=board.id,
    work_item_ids=[work_item.id]
)

# 6. Advance time
result = auth_sdk.system.advance_time_unit(organization_id=org_id)
```

---

## 📊 **Error Handling**

### Common Error Types
- `BadRequestError` (400) - Invalid request data
- `UnauthorizedError` (401, 403) - Authentication/authorization issues
- `NotFoundError` (404) - Resource not found
- `HTTPValidationError` (422) - Validation errors
- `RateLimitedError` (429) - Rate limiting
- `APIError` (4XX, 5XX) - General API errors

### Error Handling Example
```python
from dbrsdk import errors

try:
    user = sdk.users.create(
        organization_id=org_id,
        username="newuser",
        email="invalid-email",  # Invalid email format
        display_name="New User",
        password="password",
        system_role_id=role_id
    )
except errors.HTTPValidationError as e:
    print(f"Validation error: {e}")
except errors.UnauthorizedError as e:
    print(f"Permission denied: {e}")
except errors.APIError as e:
    print(f"API error: {e}")
```

---

## 🎯 **Best Practices**

### 1. **Always Use Organization Scoping**
```python
# ✅ Good - Always specify organization_id
work_items = sdk.work_items.list(organization_id=org_id)

# ❌ Bad - Missing organization context
# This will fail for most endpoints
```

### 2. **Handle Authentication Properly**
```python
# ✅ Good - Check authentication status
try:
    user_info = sdk.authentication.get_current_user_info()
    print(f"Authenticated as: {user_info.username}")
except errors.UnauthorizedError:
    print("Need to login first")
```

### 3. **Use Proper Error Handling**
```python
# ✅ Good - Specific error handling
try:
    collection = sdk.collections.create(...)
except errors.HTTPValidationError as e:
    # Handle validation errors
    pass
except errors.UnauthorizedError as e:
    # Handle permission errors
    pass
```

### 4. **Leverage Filtering and Sorting**
```python
# ✅ Good - Use filters to get specific data
active_projects = sdk.collections.list(
    organization_id=org_id,
    type="Project",
    status="active"
)

high_priority_items = sdk.work_items.list(
    organization_id=org_id,
    priority="high",
    status=["Ready", "In-Progress"]
)
```

---

## 📚 **Additional Resources**

- **API Documentation**: Available at `/docs` endpoint when running the backend
- **OpenAPI Specification**: `dbr-buffer-management-system-api.json`
- **Test Examples**: See `tests_bdd/` directory for comprehensive usage examples
- **Backend Source**: `dbr_mvp/backend/src/dbr/api/` for API implementation details

---

*This document is auto-generated from the DBR OpenAPI specification and SDK documentation. Last updated: 2025-01-20*
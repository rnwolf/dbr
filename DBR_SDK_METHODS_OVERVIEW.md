# DBR SDK Methods Overview

## 📋 **Complete API Reference for DBR Python SDK**

This document provides a comprehensive overview of all available methods in the DBR (Drum Buffer Rope) Python SDK, organized by functional area.

---

## 🚀 **Quick Start - Default Super Admin Credentials**

### **Default Super Admin User**
The backend automatically creates a default super admin user during database initialization:

- **Username**: `admin`
- **Email**: `admin@test.com`
- **Password**: `admin123`
- **Role**: Super Admin (full system access)

### **Immediate SDK Usage**
```python
from dbrsdk import Dbrsdk

# Initialize SDK and login with default super admin
sdk = Dbrsdk()

# Login to get JWT token
login_response = sdk.authentication.login(
    username="admin",
    password="admin123"
)

# Initialize authenticated SDK instance
authenticated_sdk = Dbrsdk(
    http_bearer=login_response.access_token
)

# Now you can use all SDK methods with full permissions
orgs = authenticated_sdk.organizations.get()
print(f"Available organizations: {len(orgs)}")
```

### **Default Test Environment**
The backend also creates:
- **Default Organization**: "Default Organization" (admin@default.org)
- **Additional Test Users**: orgadmin, planner, worker, viewer (all with password format: `{role}123`)
- **All users are pre-configured** as members of the default organization

**👉 Use the super admin credentials above to start testing immediately!**

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
- **LoginResponse**: `access_token`, `token_type`, `user`
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
# Create new organization
org = sdk.organizations.create(
    name="Acme Corp",
    contact_email="admin@acme.com",
    country="US",
    description="Main organization"
)

# Get all organizations
orgs = sdk.organizations.get()

# Update organization
updated_org = sdk.organizations.update(
    org_id="org-123",
    name="Acme Corporation",
    description="Updated description"
)
```

### Key Fields
- **OrganizationResponse**: `id`, `name`, `description`, `status`, `contact_email`, `country`, `subscription_level`, `default_board_id`, `created_date`, `updated_date`

---

## 👥 **Users** (`sdk.users`)

### Methods
- `get(organization_id, active_only=None, role=None)` → `List[UserResponse]`
- `create(username, email, display_name, password, organization_id, role="viewer")` → `UserResponse`
- `get_by_id(user_id, organization_id)` → `UserResponse`
- `update(user_id, organization_id, username=None, email=None, display_name=None, password=None, active_status=None)` → `UserResponse`
- `delete(user_id, organization_id)` → `Any`

### Usage Examples
```python
# Get all users in organization
users = sdk.users.get(organization_id="org-123")

# Create new user
user = sdk.users.create(
    username="john.doe",
    email="john@acme.com",
    display_name="John Doe",
    password="secure123",
    organization_id="org-123",
    role="planner"
)

# Update user
updated_user = sdk.users.update(
    user_id="user-456",
    organization_id="org-123",
    display_name="John Smith"
)
```

### Key Fields
- **UserResponse**: `id`, `username`, `email`, `display_name`, `active_status`, `created_date`, `updated_date`

---

## 🤝 **Memberships** (`sdk.memberships`)

### Methods
- `get(org_id, role=None, active_only=None)` → `List[MembershipResponse]`
- `create(org_id, user_id, role)` → `MembershipResponse`
- `get_membership(org_id, user_id)` → `MembershipResponse`
- `update_membership(org_id, user_id, role=None, active_status=None)` → `MembershipResponse`
- `delete(org_id, user_id)` → `Any`

### Usage Examples
```python
# Get all memberships in organization
memberships = sdk.memberships.get(org_id="org-123")

# Create new membership
membership = sdk.memberships.create(
    org_id="org-123",
    user_id="user-456",
    role="planner"
)

# Update membership role
updated_membership = sdk.memberships.update_membership(
    org_id="org-123",
    user_id="user-456",
    role="org_admin"
)
```

### Key Fields
- **MembershipResponse**: `id`, `organization_id`, `user_id`, `role`, `active_status`, `created_date`, `updated_date`

---

## 📦 **Collections** (`sdk.collections`)

### Methods
- `get_all(organization_id, status=None)` → `List[CollectionResponse]`
- `create(name, organization_id, description=None, status="active")` → `CollectionResponse`
- `get_by_id(collection_id, organization_id)` → `CollectionResponse`
- `update(collection_id, organization_id, name=None, description=None, status=None)` → `CollectionResponse`
- `delete(collection_id, organization_id)` → `Any`

### Usage Examples
```python
# Create new collection
collection = sdk.collections.create(
    name="Q1 Projects",
    organization_id="org-123",
    description="First quarter projects"
)

# Get all collections
collections = sdk.collections.get_all(organization_id="org-123")

# Update collection
updated_collection = sdk.collections.update(
    collection_id="col-456",
    organization_id="org-123",
    name="Q1 2024 Projects"
)
```

### Key Fields
- **CollectionResponse**: `id`, `name`, `description`, `status`, `organization_id`, `created_date`, `updated_date`

---

## 📋 **Work Items** (`sdk.work_items`)

### Methods
- `list(organization_id, collection_id=None, status=None, priority=None, sort=None, url=None)` → `List[WorkItemResponse]`
- `create(title, organization_id, description=None, collection_id=None, status="Ready", priority="Medium", estimated_total_hours=0.0, ccr_hours_required=None, estimated_sales_price=None, estimated_variable_cost=None, responsible_user_id=None, url=None)` → `WorkItemResponse`
- `get(work_item_id, organization_id)` → `WorkItemResponse`
- `update(work_item_id, organization_id, title=None, description=None, collection_id=None, status=None, priority=None, estimated_total_hours=None, ccr_hours_required=None, estimated_sales_price=None, estimated_variable_cost=None, responsible_user_id=None, url=None)` → `WorkItemResponse`
- `delete(work_item_id, organization_id)` → `Any`
- `update_task(work_item_id, task_id, organization_id, title=None, description=None, status=None, estimated_hours=None, actual_hours=None, ccr_id=None, responsible_user_id=None)` → `WorkItemResponse`

### Usage Examples
```python
# Create new work item
work_item = sdk.work_items.create(
    title="Implement user authentication",
    organization_id="org-123",
    description="Add JWT-based authentication system",
    collection_id="col-456",
    priority="High",
    estimated_total_hours=40.0
)

# Get all work items
work_items = sdk.work_items.list(
    organization_id="org-123",
    status="In-Progress"
)

# Update work item
updated_item = sdk.work_items.update(
    work_item_id="wi-789",
    organization_id="org-123",
    status="Completed"
)

# Update specific task within work item
updated_item = sdk.work_items.update_task(
    work_item_id="wi-789",
    task_id="task-123",
    organization_id="org-123",
    status="Completed",
    actual_hours=8.5
)
```

### Key Fields
- **WorkItemResponse**: `id`, `organization_id`, `collection_id`, `title`, `description`, `status`, `priority`, `estimated_total_hours`, `ccr_hours_required`, `estimated_sales_price`, `estimated_variable_cost`, `throughput`, `tasks`, `progress_percentage`, `responsible_user_id`, `url`, `created_date`, `updated_date`
- **TaskResponse**: `id`, `title`, `description`, `status`, `estimated_hours`, `actual_hours`, `ccr_id`, `responsible_user_id`

---

## 📅 **Schedules** (`sdk.schedules`)

### Methods
- `list(organization_id, board_config_id=None, status=None)` → `List[ScheduleResponse]`
- `create(organization_id, board_config_id, work_item_ids, capability_channel_id=None, time_unit_position=None, timezone="UTC")` → `ScheduleResponse`
- `get(schedule_id, organization_id)` → `ScheduleResponse`
- `update(schedule_id, organization_id, board_config_id=None, work_item_ids=None, capability_channel_id=None, status=None, time_unit_position=None, timezone=None)` → `ScheduleResponse`
- `delete(schedule_id, organization_id)` → `Any`
- `get_board_analytics(board_config_id, organization_id)` → `BoardAnalytics`

### Usage Examples
```python
# Create new schedule
schedule = sdk.schedules.create(
    organization_id="org-123",
    board_config_id="board-456",
    work_item_ids=["wi-1", "wi-2", "wi-3"],
    capability_channel_id="channel-789",
    time_unit_position=0
)

# Get all schedules
schedules = sdk.schedules.list(
    organization_id="org-123",
    status="Active"
)

# Get board analytics
analytics = sdk.schedules.get_board_analytics(
    board_config_id="board-456",
    organization_id="org-123"
)
```

### Key Fields
- **ScheduleResponse**: `id`, `organization_id`, `board_config_id`, `capability_channel_id`, `status`, `work_item_ids`, `time_unit_position`, `total_ccr_time`, `timezone`, `created_date`, `released_date`, `completion_date`
- **BoardAnalytics**: Analytics data for board performance metrics

---

## 📊 **Analytics** (`sdk.schedules.analytics`)

### Methods
- `get(schedule_id, organization_id)` → `ScheduleAnalytics`

### Usage Examples
```python
# Get schedule analytics
analytics = sdk.schedules.analytics.get(
    schedule_id="sched-123",
    organization_id="org-123"
)
```

### Key Fields
- **ScheduleAnalytics**: Detailed analytics for specific schedule performance

---

## ⚙️ **System Operations** (`sdk.system`)

### Methods
- `advance_time_unit(organization_id, board_config_id=None)` → `AdvanceTimeResponse`
- `get_time()` → `Dict[str, Any]`
- `set_time(time_iso)` → `Dict[str, Any]`

### Usage Examples
```python
# Advance time for all schedules (DBR core operation)
result = sdk.system.advance_time_unit(
    organization_id="org-123"
)

# Get current system time
current_time = sdk.system.get_time()

# Set system time (for testing)
sdk.system.set_time(time_iso="2024-01-15T10:00:00Z")
```

### Key Fields
- **AdvanceTimeResponse**: Results of time advancement operation including affected schedules

---

## 🏥 **Health Checks**

### Basic Health (`sdk.health`)
- `get()` → `Any` - Basic service health check

### API Health (`sdk.api_health`)
- `get()` → `Any` - API-specific health check

### Usage Examples
```python
# Basic health check
health_status = sdk.health.get()

# API health check
api_health = sdk.api_health.get()
```

---

## 🔐 **Security & Authentication**

### SDK Initialization
```python
from dbrsdk import Dbrsdk

# Initialize with bearer token
sdk = Dbrsdk(
    http_bearer="your_jwt_token_here"
)

# Or use context manager
with Dbrsdk(http_bearer="your_jwt_token") as sdk:
    # Your API calls here
    pass
```

### Error Handling
All SDK methods can raise the following exceptions:
- `errors.BadRequestError` (400)
- `errors.UnauthorizedError` (401, 403)
- `errors.NotFoundError` (404)
- `errors.HTTPValidationError` (422)
- `errors.RateLimitedError` (429)
- `errors.APIError` (4XX, 5XX)

### Retry Configuration
```python
from dbrsdk.utils import RetryConfig

# Custom retry configuration
retry_config = RetryConfig(
    strategy="backoff",
    backoff_factor=1.5,
    retry_connection_errors=True
)

# Use with any method
result = sdk.work_items.list(
    organization_id="org-123",
    retries=retry_config
)
```

---

## 🚀 **Quick Start Workflow**

```python
from dbrsdk import Dbrsdk

# 1. Initialize SDK
sdk = Dbrsdk(http_bearer="your_token")

# 2. Login (if needed)
login_response = sdk.authentication.login(
    username="admin",
    password="admin123"
)

# 3. Get organizations
orgs = sdk.organizations.get()
org_id = orgs[0].id

# 4. Create collection
collection = sdk.collections.create(
    name="My Project",
    organization_id=org_id
)

# 5. Create work item
work_item = sdk.work_items.create(
    title="Sample Task",
    organization_id=org_id,
    collection_id=collection.id,
    estimated_total_hours=8.0
)

# 6. Create schedule
schedule = sdk.schedules.create(
    organization_id=org_id,
    board_config_id="default-board",
    work_item_ids=[work_item.id]
)

# 7. Advance time (DBR operation)
result = sdk.system.advance_time_unit(organization_id=org_id)
```

---

## 📚 **Additional Resources**

- **OpenAPI Specification**: Available in `dbr_mvp/backend/dbr-buffer-management-system-api.json`
- **Model Documentation**: Detailed field descriptions in `dbrsdk-python/docs/models/`
- **Error Documentation**: Error handling details in `dbrsdk-python/docs/errors/`
- **SDK Source**: Complete SDK source code in `dbrsdk-python/src/dbrsdk/`

---

*This document is auto-generated from the DBR OpenAPI specification and SDK documentation. Last updated: 2025-01-20*
# DBR Test Data and Credentials Reference

## 👥 **Default Test Users Created by Database Initialization**

| Username | Email | Password | Role | Description |
|----------|-------|----------|------|-------------|
| `admin` | admin@test.com | `admin123` | **Super Admin** | Full system access, can manage all organizations |
| `orgadmin` | orgadmin@test.com | `orgadmin123` | **Organization Admin** | Can manage users and settings within their organization |
| `planner` | planner@test.com | `planner123` | **Planner** | Can create/manage work items, schedules, advance time |
| `worker` | worker@test.com | `worker123` | **Worker** | Can update work items and view reports |
| `viewer` | viewer@test.com | `viewer123` | **Viewer** | Read-only access to reports and dashboards |

## 🏢 **Default Organization**

- **Name**: "Default Organization"
- **Description**: "Default organization for MVP testing and development"
- **Status**: Active
- **Contact Email**: admin@default.org
- **Country**: US
- **Subscription Level**: basic

## 🔐 **Role Hierarchy and Permissions**

### **Super Admin** (admin@test.com)
- **System-wide permissions**: Can manage all organizations
- **Cross-organization access**: Can view and manage any organization
- **User management**: Can create organizations and assign organization admins
- **Global settings**: Can manage system-wide configurations

### **Organization Admin** (orgadmin@test.com)
- **Organization scope**: Limited to "Default Organization"
- **User management**: Can invite users to their organization
- **Role assignment**: Can assign roles within their organization
- **Organization settings**: Can modify organization details
- **Board configuration**: Can set up DBR boards and CCRs

### **Planner** (planner@test.com)
- **Work item management**: Can create, edit, and manage work items
- **Schedule management**: Can create and manage schedules
- **Time progression**: Can advance time units
- **Planning operations**: Can bundle work items into schedules
- **CCR management**: Can view and plan around capacity constraints

### **Worker** (worker@test.com)
- **Work item updates**: Can update status and progress of assigned work items
- **Task execution**: Can mark tasks as complete
- **Report viewing**: Can view reports related to their work
- **Limited editing**: Cannot create new work items or schedules

### **Viewer** (viewer@test.com)
- **Read-only access**: Can view all reports and dashboards
- **No editing**: Cannot modify any data
- **Monitoring**: Can observe system performance and metrics
- **Reporting**: Can generate and view reports

## 🔗 **Organization Membership Configuration**

### **Membership Details**
- **Organization**: All users are members of "Default Organization"
- **Invitation Status**: All memberships are pre-accepted (no pending invitations)
- **Inviter**: All users were "invited" by the admin user
- **Join Date**: Set to current timestamp during initialization
- **Role Mapping**: Each user's organization role matches their system role

### **Membership Structure**
```
Default Organization
├── admin@test.com (Super Admin)
├── orgadmin@test.com (Organization Admin) 
├── planner@test.com (Planner)
├── worker@test.com (Worker)
└── viewer@test.com (Viewer)
```

## 🧪 **Testing with Different User Roles**

### **Authentication Examples**
```python
# Super Admin Login
client.authentication.login(username="admin", password="admin123")

# Organization Admin Login  
client.authentication.login(username="orgadmin", password="orgadmin123")

# Planner Login
client.authentication.login(username="planner", password="planner123")

# Worker Login
client.authentication.login(username="worker", password="worker123")

# Viewer Login
client.authentication.login(username="viewer", password="viewer123")
```

### **Role-Based Testing Scenarios**

#### **Super Admin Tests**
- Can access all organizations
- Can create new organizations
- Can manage global system settings
- Can assign organization admins

#### **Organization Admin Tests**
- Can manage "Default Organization" settings
- Can invite new users to the organization
- Can assign roles within the organization
- Can configure DBR boards and CCRs
- Cannot access other organizations

#### **Planner Tests**
- Can create and manage work items
- Can create schedules and bundle work items
- Can advance time units
- Can view CCR capacity and loading
- Cannot manage users or organization settings

#### **Worker Tests**
- Can update assigned work items
- Can mark tasks as complete
- Can view relevant reports
- Cannot create new work items or schedules
- Cannot access planning functions

#### **Viewer Tests**
- Can view all reports and dashboards
- Cannot modify any data
- Cannot access management functions
- Read-only access to all visible content

## 🎯 **Frontend Navigation Implications**

### **Navigation Visibility by Role**

| Feature | Super Admin | Org Admin | Planner | Worker | Viewer |
|---------|-------------|-----------|---------|--------|--------|
| Organizations Management | ✅ | ❌ | ❌ | ❌ | ❌ |
| User Management | ✅ | ✅ | ❌ | ❌ | ❌ |
| Setup Workflow | ✅ | ✅ | ❌ | ❌ | ❌ |
| Work Items | ✅ | ✅ | ✅ | ✅ (assigned) | ✅ (read-only) |
| Collections | ✅ | ✅ | ✅ | ✅ (assigned) | ✅ (read-only) |
| Planning | ✅ | ✅ | ✅ | ❌ | ✅ (read-only) |
| Buffer Boards | ✅ | ✅ | ✅ | ✅ (execution) | ✅ (read-only) |
| Reports | ✅ | ✅ | ✅ | ✅ (limited) | ✅ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |
| Time Progression | ✅ | ✅ | ✅ | ❌ | ❌ |

## 📝 **Database Initialization Process**

1. **Create Tables**: All database tables are created
2. **Create Default Organization**: "Default Organization" is established
3. **Create System Roles**: All 5 role types are defined
4. **Create Test Users**: All 5 test users are created with hashed passwords
5. **Create Memberships**: All users are added to the default organization
6. **Set Permissions**: Role-based permissions are established

## 🔄 **Regenerating Test Data**

To reset the test data:
1. Delete the `dbr.db` file
2. Restart the backend server
3. Database initialization will recreate all default data

## 🚀 **Ready for Phase 5 Implementation**

With this test data structure, we can now:
- Test role-based navigation in the frontend
- Validate organization context switching
- Test the complete DBR workflow from setup to execution
- Verify permission-based feature access
- Test multi-user collaboration scenarios

---

*Generated from DBR backend database initialization analysis*
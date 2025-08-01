# Updated Frontend Development Phases (5-8)
## Based on Completed Backend and Updated Buffer Board Components Specification

### Current Status Assessment
✅ **Backend Complete**: All APIs implemented, tested, and secured
✅ **Authentication System**: JWT-based auth with role-based permissions  
✅ **Core Business Logic**: DBR Engine, Time Progression, Schedule Management
✅ **Security Audit**: All endpoints properly secured
✅ **Template Ready**: tkinter-template available for frontend foundation

---

## Phase 5: Frontend Foundation (Days 15-16)

### Current Frontend Status Assessment
✅ **CustomTkinter Template Complete**: Professional GUI foundation with modern architecture
✅ **Core Components Ready**: Tab navigation, scrollable canvas, event bus, testing framework
✅ **Development Infrastructure**: UV dependency management, pytest, code quality tools
✅ **DBR SDK Validated**: Professional auto-generated SDK with authentication working
✅ **Backend Enhanced**: Comprehensive logging, health checks, 5 test users with roles
✅ **Test Environment**: Complete multi-user setup with Default Organization
✅ **Step 5.1 Complete**: DBR Application Bootstrap & Startup Sequence (DONE)
✅ **Step 5.2 Complete**: DBR Service Layer with SDK Integration (DONE)
✅ **Step 5.3 Complete**: Authentication UI with Test User Integration (DONE)
✅ **Step 5.4 Complete**: Role-Based Navigation with Test User Validation (DONE)

### DBR Organization Admin Workflow (Refined)

#### **Phase 1: Organization Setup (Sequential Dependencies)**
1. **User Management/Membership** → Invite users, assign roles
2. **CCR Setup** → Define Capacity Constrained Resources (requires users)
3. **Time Unit & Calendar Setup** → Define time periods, working calendars  
4. **DBR Board Setup** → Configure buffer zones, capability channels (requires CCRs)

#### **Phase 2: Content Management (Parallel Activities)**
5. **Work Items Management** → Create/edit individual tasks
6. **Collections Management** → Group work items into projects/epics/releases

#### **Phase 3: Planning Operations (Ongoing Cycle)**
7. **Schedule Planning** → Bundle work items into time-unit schedules
   - Select Capability Channel (CCR)
   - Sequence work items into schedules
   - Get real-time CCR loading feedback
   - Validate capacity constraints

#### **Phase 4: Execution Operations (Ongoing Cycle)**
8. **Schedule Release** → Move Ready schedules into active capability channels
9. **Operational Updates** → Track work item progress and status

### Application Startup Workflow
1. **Application Launch** → Backend URL Configuration Dialog
2. **Health Check** → Verify API connectivity and display status
3. **Authentication** → User login with role detection
4. **Organization Context** → Single org optimization, multi-org capability
5. **Role-Based Navigation** → Dynamic UI based on user permissions
6. **Setup State Detection** → Progressive disclosure based on completion

### Day 5A: Application Architecture Setup (4 hours)

#### Step 5.1: DBR Application Bootstrap & Startup Sequence (2 hours)
**Objective**: Transform generic template into DBR-specific application with proper startup flow

**TDD Cycle:**
```python
# tests/test_frontend/test_dbr_startup.py
def test_backend_url_configuration():
    """Test backend URL configuration dialog"""
    # Test: URL input validation
    # Test: Health check integration
    # Test: Configuration persistence

def test_health_check_workflow():
    """Test API health check functionality"""
    # Test: Successful connection detection
    # Test: Failed connection handling
    # Test: Connection status display

def test_application_branding():
    """Test DBR application branding"""
    # Test: Window title updated to DBR
    # Test: Menu structure reflects DBR operations
    # Test: Status bar shows DBR context
```

**Implementation Tasks:**
- Rename application from "CustomTkinter Template" to "DBR Buffer Management System"
- Create backend URL configuration dialog with health check
- Update AppConfig for DBR-specific settings (window title, default sizes)
- Implement startup sequence manager with progressive UI reveal
- Add connection status indicators and error handling

#### ✅ Step 5.2: DBR Service Layer with SDK Integration (2 hours) - COMPLETE
**Objective**: Create frontend service layer wrapping the validated DBR SDK

**✅ COMPLETED - All Tests Passing:**
```python
# tests/test_dbr_service.py - 10/10 tests PASSING
✅ test_authentication_service_login_success
✅ test_health_check_success  
✅ test_health_check_failure
✅ test_health_check_invalid_response
✅ test_organization_context_setup
✅ test_role_based_permissions
✅ test_super_admin_permissions
✅ test_viewer_permissions
✅ test_logout_clears_context
✅ test_connection_status
```

**✅ Implementation Complete:**
- ✅ **DBR SDK Integration**: Successfully integrated as frontend dependency
- ✅ **Enhanced DBRService Class**: Comprehensive service layer with frontend-specific features
- ✅ **Authentication Flow**: Working login with test user credentials (admin/admin123)
- ✅ **Organization Context**: Auto-selects "Default Organization" after login
- ✅ **Role-Based Permissions**: Framework ready for 5 user roles (Super Admin, Org Admin, Planner, Worker, Viewer)
- ✅ **Health Check Integration**: Backend connectivity validation using SDK endpoints
- ✅ **Session Management**: Clean logout with context clearing
- ✅ **Connection Status**: Comprehensive status reporting for UI integration
- ✅ **Error Handling**: User-friendly error messages and exception handling

**✅ Validation Results:**
- Backend health check: ✅ PASS
- Authentication with admin/admin123: ✅ SUCCESS  
- Organization context setup: ✅ WORKING
- Authenticated SDK client: ✅ AVAILABLE
- Session management: ✅ FUNCTIONAL

### Day 5B: Authentication & Navigation Development (4 hours)

#### ✅ Step 5.3: Authentication UI with Test User Integration (COMPLETED)
**Objective**: Build login interface integrated with test user credentials and role detection

**✅ COMPLETED - All Tests Passing (22/22):**
```python
# tests/test_authentication_ui.py - 10/10 tests PASSING
✅ test_login_dialog_initialization
✅ test_login_dialog_with_test_users  
✅ test_login_dialog_invalid_credentials
✅ test_role_detection_and_caching
✅ test_session_persistence_setup
✅ test_user_context_widget_creation
✅ test_user_context_display_formatting
✅ test_complete_authentication_workflow
✅ test_authentication_failure_handling
✅ test_test_user_credential_hints

# tests/test_dbr_service.py - 10/10 tests PASSING
✅ test_authentication_service_login_success
✅ test_health_check_success
✅ test_health_check_failure
✅ test_health_check_invalid_response
✅ test_organization_context_setup
✅ test_role_based_permissions
✅ test_super_admin_permissions
✅ test_viewer_permissions
✅ test_logout_clears_context
✅ test_connection_status

# tests/test_dbr_startup.py - 2/2 tests PASSING
✅ test_application_branding
✅ test_startup_sequence_and_health_check
```

**✅ Implementation Complete:**
- ✅ **Professional LoginDialog**: Backend health checking, test user hints, error handling
- ✅ **Test User Integration**: 5 test users with role hierarchy (Super Admin → Org Admin → Planner → Viewer)
- ✅ **Role-Based Permission System**: Granular permission checking with `has_permission()` method
- ✅ **UserContextWidget**: Displays user info, role, and organization context in main window
- ✅ **AuthenticationManager**: Complete workflow orchestration from login to main window
- ✅ **Session Management**: Token storage, authentication context, clean logout
- ✅ **SDK Integration**: Full integration with DBR SDK for authentication and API calls
- ✅ **Organization Context**: Auto-selection of "Default Organization" after login
- ✅ **Comprehensive Error Handling**: User-friendly error messages and connection validation

**✅ Test User Credentials Validated:**
- **Super Admin**: `admin` / `admin123` (Full system access)
- **Organization Admin**: `orgadmin` / `orgadmin123` (Organization management)
- **Organization Admin**: `testuser` / `testpassword123` (Alternative org admin)
- **Planner**: `planner` / `planner123` (Schedule and work item management)
- **Viewer**: `viewer2` / `viewer123` (Read-only access)

**✅ Role-Based Permissions Implemented:**
- **Super Admin**: All permissions (`*`) including cross-organization management
- **Organization Admin**: `manage_organization`, `manage_users`, `manage_user_roles`, `invite_users`, `manage_ccrs`, `manage_schedules`, `manage_work_items`, `manage_collections`, `view_analytics`, `manage_organization_settings`
- **Planner**: `manage_schedules`, `manage_work_items`, `manage_collections`, `view_analytics`, `view_users`, `view_ccrs`
- **Viewer**: `view_schedules`, `view_work_items`, `view_collections`, `view_analytics`, `view_users`, `view_ccrs`

**✅ Ready for Step 5.4**: Role-based navigation foundation complete

#### Step 5.4: Role-Based Navigation with Test User Validation (2 hours)
**Objective**: Implement dynamic navigation validated with actual test user roles

**TDD Cycle:**
```python
# tests/test_frontend/test_role_navigation.py
def test_super_admin_navigation():
    """Test Super Admin navigation (admin@test.com)"""
    # Test: All tabs visible (Setup, Work Items, Collections, Planning, Buffer Boards, Reports)
    # Test: System management menu items visible
    # Test: Organization management accessible
    # Test: Global time progression controls

def test_org_admin_navigation():
    """Test Organization Admin navigation (orgadmin@test.com)"""
    # Test: Setup tab visible (user management, CCR setup, board config)
    # Test: Work Items, Collections, Planning, Buffer Boards, Reports visible
    # Test: Organization settings accessible
    # Test: User invitation capabilities

def test_planner_navigation():
    """Test Planner navigation (planner@test.com)"""
    # Test: Work Items, Collections, Planning, Buffer Boards, Reports visible
    # Test: Setup tab hidden (no user management access)
    # Test: Schedule creation and management accessible
    # Test: Time progression controls available

def test_worker_navigation():
    """Test Worker navigation (worker@test.com)"""
    # Test: Work Items (assigned only), Buffer Boards (execution), Reports (limited)
    # Test: Collections visible but read-only for assigned items
    # Test: Planning tab hidden
    # Test: Setup tab hidden

def test_viewer_navigation():
    """Test Viewer navigation (viewer@test.com)"""
    # Test: Buffer Boards (read-only), Reports visible
    # Test: Work Items visible but read-only
    # Test: Planning, Setup tabs hidden
    # Test: No editing capabilities anywhere
```

**Implementation Tasks:**
- Replace generic "Grid View/Settings" tabs with role-based DBR navigation
- Implement navigation visibility matrix:
  - **Super Admin**: All tabs (Setup, Work Items, Collections, Planning, Buffer Boards, Reports, System)
  - **Org Admin**: Setup, Work Items, Collections, Planning, Buffer Boards, Reports
  - **Planner**: Work Items, Collections, Planning, Buffer Boards, Reports
  - **Worker**: Work Items (assigned), Buffer Boards (execution), Reports (limited)
  - **Viewer**: Buffer Boards (read-only), Reports (read-only)
- Add "Default Organization" context indicator in top-right
- Update menu structure with role-appropriate options
- Implement setup completion detection for progressive disclosure
- Add user role indicator and logout option in menu bar

### Navigation Structure by Role

#### **Super Admin Navigation:**
- Organizations (manage all organizations)
- Users (global user management)
- System (global settings, time progression)

#### **Organization Admin Navigation:**
- Setup (Users→CCRs→Time Units→Board Config)
- Work Items & Collections
- Planning & Buffer Boards
- Reports

#### **Planner Navigation:**
- Work Items & Collections
- Planning (schedule creation)
- Buffer Boards (planning view)
- Reports (planning metrics)

#### **Worker Navigation:**
- Work Items (assigned tasks)
- Buffer Boards (execution view)
- Reports (personal metrics)

### Setup Completion Detection
- **Phase 1 Complete**: Users invited, CCRs defined, time units configured, board setup
- **Phase 2 Ready**: Work items and collections can be created
- **Phase 3 Ready**: Planning and scheduling can begin
- **Phase 4 Ready**: Operational execution can start

---

## Updated Phase 5 Summary (SDK-Leveraged Approach)

### **Key Changes from Original Plan:**
1. **SDK Integration**: Leverages professional auto-generated SDK instead of custom API client
2. **Test User Validation**: All development validated with actual test users and roles
3. **Role-Based Architecture**: Navigation and permissions based on 5 distinct user roles
4. **Default Organization**: Optimized for single organization with multi-org capability
5. **Enhanced Backend**: Comprehensive logging and health checks for debugging

### **SDK Benefits Realized:**
- **60-70% Development Time Saved**: No custom API client, authentication, or data models needed
- **Type Safety**: Full IDE support with Pydantic models and error handling
- **Professional Error Handling**: Built-in retry logic, timeouts, and exception hierarchy
- **Automatic Backend Sync**: SDK regenerates when backend API changes
- **Async Support**: Perfect for non-blocking GUI operations

### **Dependencies Resolved:**
- Step 5.1 creates DBR-branded application with startup sequence
- Step 5.2 wraps SDK in frontend service layer with organization context
- Step 5.3 integrates SDK authentication with test user credentials
- Step 5.4 creates role-validated navigation with actual permission testing

### **Test Environment Ready:**
- **5 Test Users**: admin, orgadmin, planner, worker, viewer with known credentials
- **Default Organization**: Complete membership setup for all users
- **Role Validation**: Each navigation feature tested with appropriate user roles
- **Backend Logging**: Enhanced debugging for frontend-backend integration

### **Next Phase Preparation:**
Phase 5 establishes the foundation for Phase 6 (Organization Setup Workflow) by providing:
- SDK-integrated service layer with authentication and organization context
- Role-based navigation validated with test users
- Complete test environment with 5 user roles and Default Organization
- Enhanced backend logging for debugging setup workflows

**Phase 5 is now complete.**

---

## Phase 6: Organization Setup Workflow (Days 17-19)
**MVP Approach for User Management**: For the MVP, "inviting" a user will mean an administrator directly creates the user and sets a temporary password. The administrator will be responsible for communicating these credentials to the user out-of-band (e.g., via a separate email or message). Full email integration for invitations and password resets will be deferred to Phase 9.

### Day 6A: User Management Setup (4 hours)
#### Step 6.1: User Invitation & Role Assignment Interface (2 hours)
**Objective**: Create an interface for Org Admins to create new users and assign roles.

**TDD Cycle:**
```python
# tests/test_user_management.py
def test_user_creation_form_display():
    """Test that the user creation form displays correctly."""
    # Test: Form has fields for username, password, and role.
    # Test: Role dropdown is populated with available roles.
    # Test: "Create User" button is present.

def test_user_creation_success():
    """Test successful user creation."""
    # Test: Calling the create_user method on the DBR service.
    # Test: A success message is displayed.
    # Test: The user list is refreshed.

def test_user_creation_validation():
    """Test form validation for user creation."""
    # Test: Username is required.
    # Test: Password is required and meets complexity rules.
    # Test: Role is required.

def test_user_creation_api_error():
    """Test handling of API errors during user creation."""
    # Test: An error message is displayed if the API call fails.
    # Test: The form is not cleared on failure.
```

**Implementation Tasks:**
- Create a `UserManagementPage` that will be shown in the "Setup" tab.
- Design a `CreateUserDialog` with fields for username, temporary password, and role selection.
- Populate the role selection dropdown with the available roles (excluding Super Admin for Org Admins).
- Implement form validation for all fields.
- Connect the "Create User" button to the `dbr_service.create_user` method.
- Display appropriate success or error messages to the user.
- Refresh the user list upon successful creation.
#### Step 6.2: Organization Membership Management (2 hours)

### Day 6B: CCR & Time Unit Configuration (4 hours)  
#### Step 6.3: CCR Definition Interface (2 hours)
#### Step 6.4: Time Unit & Calendar Setup (2 hours)

### Day 6C: Board Configuration Setup (4 hours)
#### Step 6.5: Buffer Zone Configuration (2 hours)
#### Step 6.6: Capability Channel Setup (2 hours)

**TDD Cycle:**
```python
# tests/test_frontend/test_login_window.py
def test_login_window_display():
    """Test login window functionality"""
    # Test: Login form displays correctly
    # Test: Username/password validation
    # Test: Login button functionality

def test_authentication_flow():
    """Test complete authentication process"""
    # Test: Valid login opens main window
    # Test: Invalid credentials show error
    # Test: Token persistence across sessions
    # Test: Organization context after login

def test_role_based_interface():
    """Test role-based UI elements"""
    # Test: Super User sees organization management
    # Test: Other roles see organization selection only
    # Test: Role-appropriate menu options
```

**Implementation Tasks:**
- Create `LoginWindow` using CustomTkinter
- Implement form validation
- Add authentication flow with API client
- Handle login errors gracefully
- Add organization context establishment after login
- Implement role-based UI element visibility

---

## Phase 6: Buffer Board Components (Days 17-19)

### Day 6A: Board Navigation & Controls (4 hours)

#### Step 6.1: Board Navigation Component (2 hours)
**Objective**: Implement tab navigation for multiple boards

**TDD Cycle:**
```python
# tests/test_frontend/test_board_navigation.py
def test_board_tab_navigation():
    """Test board navigation tabs"""
    # Test: Multiple board tabs display
    # Test: Switch between boards
    # Test: Active board highlighting

def test_board_configuration_loading():
    """Test board config loading"""
    # Test: Load board configurations from API
    # Test: Display board names and settings
    # Test: Handle missing/invalid boards
```

**Implementation Tasks:**
- Create `BoardNavigationComponent` based on specification
- Implement tab switching functionality
- Load board configurations from API
- Add board selection persistence

#### Step 6.2: Time Controls Component (2 hours)
**Objective**: Implement time progression controls as specified

**TDD Cycle:**
```python
# tests/test_frontend/test_time_controls.py
def test_time_display():
    """Test time display functionality"""
    # Test: Current time display with timezone
    # Test: Next time unit display
    # Test: Real-time clock updates

def test_time_progression_controls():
    """Test time control buttons"""
    # Test: Fast Forward button
    # Test: Play/Pause functionality
    # Test: Manual time setting
```

**Implementation Tasks:**
- Create `TimeControlsComponent` matching specification design
- Implement real-time clock display with seconds
- Add Fast Forward button for time progression
- Create Play/Pause controls for board clock
- Display timezone and next time unit information

### Day 6B: Buffer Board Grid Foundation (4 hours)

#### Step 6.3: Buffer Board Layout (2 hours)
**Objective**: Create the core buffer board grid structure

**TDD Cycle:**
```python
# tests/test_frontend/test_buffer_board_layout.py
def test_buffer_board_grid():
    """Test buffer board grid structure"""
    # Test: Time slot columns created
    # Test: CCR rows displayed
    # Test: Zone color coding (red/yellow/green)

def test_header_rows():
    """Test configurable header rows"""
    # Test: Cell Zones row
    # Test: Cell Variance row  
    # Test: Cell Index row
    # Test: Total buffer zones row
    # Test: Total buffer percent row
```

**Implementation Tasks:**
- Create `BufferBoardComponent` with grid layout
- Implement configurable header rows as specified
- Add zone color coding (Zone 0-Black, Zone 1-Red, Zone 2-Yellow, Zone 3-Green, CCR-Light Blue)
- Create footer row with color legend

#### Step 6.4: Capability Channels (CCR Rows) (2 hours)
**Objective**: Implement CCR rows with schedule display

**TDD Cycle:**
```python
# tests/test_frontend/test_capability_channels.py
def test_ccr_row_display():
    """Test CCR row functionality"""
    # Test: CCR information display
    # Test: Schedule positioning in cells
    # Test: Multiple schedules per CCR

def test_ccr_status_component():
    """Test CCR status indicators"""
    # Test: Real-time health indicators
    # Test: Performance metrics display
    # Test: Alert integration
```

**Implementation Tasks:**
- Create `CapabilityChannelRow` components
- Implement `CCRStatusComponent` as specified
- Add schedule display within grid cells
- Create real-time status indicators

### Day 6C: Schedule Display & Interaction (4 hours)

#### Step 6.5: Schedule Cell Display (2 hours)
**Objective**: Display schedules within buffer board cells

**TDD Cycle:**
```python
# tests/test_frontend/test_schedule_display.py
def test_schedule_cell_rendering():
    """Test schedule display in cells"""
    # Test: Schedule appears in correct position
    # Test: Work item summary visible
    # Test: Progress indicators shown

def test_schedule_interaction():
    """Test schedule click interactions"""
    # Test: Click opens schedule detail
    # Test: Hover shows tooltip
    # Test: Context menu for actions
```

**Implementation Tasks:**
- Create `ScheduleCellWidget` for individual schedules
- Implement schedule positioning based on time_unit_position
- Add progress visualization and work item summaries
- Create click-to-detail functionality

#### Step 6.6: Time Progression Integration (2 hours)
**Objective**: Connect time controls to board updates

**TDD Cycle:**
```python
# tests/test_frontend/test_time_progression.py
def test_time_progression_effects():
    """Test board updates after time progression"""
    # Test: Schedules move left after advancement
    # Test: Completed schedules removed
    # Test: Buffer board refreshes correctly

def test_automatic_updates():
    """Test real-time board updates"""
    # Test: Periodic data refresh
    # Test: Visual update animations
    # Test: Conflict resolution
```

**Implementation Tasks:**
- Connect time progression API to board updates
- Implement automatic board refresh after time advancement
- Add visual feedback for time progression
- Handle real-time updates and data synchronization

---

## Phase 7: Work Item Management & Planning (Days 20-21)

### Day 7A: Organization Management & Work Items Panel (4 hours)

#### Step 7.0: Organization Management Interface (2 hours)
**Objective**: Create organization CRUD interface for Super Users

**TDD Cycle:**
```python
# tests/test_frontend/test_organization_management.py
def test_organization_list_view():
    """Test organization management interface"""
    # Test: List all organizations (Super User only)
    # Test: Organization status indicators
    # Test: Search and filter organizations

def test_organization_crud_operations():
    """Test organization CRUD functionality"""
    # Test: Create new organization
    # Test: Edit organization details
    # Test: Delete/archive organization
    # Test: Organization status management

def test_organization_selection():
    """Test organization context switching"""
    # Test: Select active organization
    # Test: Switch between organizations
    # Test: Data scoping per organization
```

**Implementation Tasks:**
- Create `OrganizationManagementWindow` for Super Users
- Implement organization CRUD operations
- Add organization selection/switching functionality
- Create organization context management
- Add role-based access control (Super User only for CRUD)

### Day 7A (continued): Available Work Items Panel (2 hours)

#### Step 7.1: Work Items Panel Component (2 hours)
**Objective**: Create work items management panel as specified

**TDD Cycle:**
```python
# tests/test_frontend/test_work_items_panel.py
def test_work_items_filtering():
    """Test work item filtering capabilities"""
    # Test: Filter by project, priority, CCR resource
    # Test: Filter by estimated hours, dependencies
    # Test: Search functionality

def test_work_items_display():
    """Test work item display features"""
    # Test: Partial scheduling status shown
    # Test: Remaining effort display
    # Test: Dependency indicators
```

**Implementation Tasks:**
- Create `AvailableWorkItemsPanel` component
- Implement filtering by project, priority, CCR resource, hours, dependencies
- Add partial scheduling status indicators
- Display remaining effort for each work item
- Create dependency information visualization

#### Step 7.2: Work Item Detail Management (2 hours)
**Objective**: Implement work item CRUD operations

**TDD Cycle:**
```python
# tests/test_frontend/test_work_item_detail.py
def test_work_item_creation():
    """Test work item creation interface"""
    # Test: Create new work item form
    # Test: Field validation
    # Test: Save to backend API

def test_work_item_editing():
    """Test work item modification"""
    # Test: Edit existing work items
    # Test: Task management
    # Test: Status updates
```

**Implementation Tasks:**
- Create `WorkItemDetailWindow` for editing
- Implement work item creation and editing forms
- Add task management functionality
- Connect to work items API endpoints

### Day 7B: Schedule Builder & Planning (4 hours)

#### Step 7.3: Schedule Builder Panel (2 hours)
**Objective**: Create schedule building interface

**TDD Cycle:**
```python
# tests/test_frontend/test_schedule_builder.py
def test_schedule_builder_interface():
    """Test schedule building functionality"""
    # Test: Multi-schedule view display
    # Test: Partial work item allocation
    # Test: Capacity tracking per schedule

def test_cross_schedule_operations():
    """Test cross-schedule functionality"""
    # Test: Move allocations between schedules
    # Test: Capacity validation
    # Test: Schedule creation and deletion
```

**Implementation Tasks:**
- Create `ScheduleBuilderPanel` component
- Implement multi-schedule view display
- Add partial work item allocation interface
- Create individual capacity meters for each draft schedule
- Enable cross-schedule movement of work item allocations

#### Step 7.4: Planning Interface Integration (2 hours)
**Objective**: Connect planning to buffer board

**TDD Cycle:**
```python
# tests/test_frontend/test_planning_integration.py
def test_planning_to_board_flow():
    """Test planning to board integration"""
    # Test: Move schedules from planning to board
    # Test: Capacity validation before release
    # Test: Planning zone interactions

def test_drag_drop_limitations():
    """Test drag-and-drop constraints"""
    # Test: Only within Planning zone
    # Test: Buffer zones prevent manual repositioning
    # Test: Time progression controls movement
```

**Implementation Tasks:**
- Integrate schedule builder with buffer board
- Implement planning zone drag-and-drop (limited scope)
- Add capacity validation before schedule release
- Enforce "time never stops" principle in buffer zones

---

## Phase 8: Integration & Polish (Days 22-23)

### Day 8A: Complete Integration Testing (4 hours)

#### Step 8.1: End-to-End Workflows (2 hours)
**Objective**: Test complete user workflows

**TDD Cycle:**
```python
# tests/test_integration/test_complete_workflows.py
def test_complete_dbr_workflow():
    """Test full DBR workflow"""
    # Test: Work item creation → Ready → Planning → Schedule → Progress → Complete
    # Test: Multiple CCR coordination
    # Test: Time progression effects

def test_standup_meeting_workflow():
    """Test standup meeting process"""
    # Test: Review all schedules
    # Test: Mark completions
    # Test: Time progression at end
```

**Implementation Tasks:**
- Create comprehensive integration tests
- Test complete work item lifecycle
- Verify standup meeting workflow
- Validate time progression effects

#### Step 8.2: Error Handling & Polish (2 hours)
**Objective**: Robust error handling and UI polish

**TDD Cycle:**
```python
# tests/test_integration/test_error_handling.py
def test_network_resilience():
    """Test frontend resilience to API failures"""
    # Test: Backend unavailable scenarios
    # Test: Timeout handling
    # Test: Graceful degradation

def test_data_consistency():
    """Test data synchronization"""
    # Test: Concurrent user scenarios
    # Test: Data refresh mechanisms
    # Test: Conflict resolution
```

**Implementation Tasks:**
- Implement comprehensive error handling
- Add graceful degradation for API failures
- Create data synchronization mechanisms
- Polish UI interactions and feedback

### Day 8B: Performance & Deployment (4 hours)

#### Step 8.3: Performance Optimization (2 hours)
**Objective**: Optimize frontend performance

**Tasks:**
- Optimize buffer board rendering for large datasets
- Implement efficient data caching
- Add loading indicators and progressive updates
- Optimize API call patterns

#### Step 8.4: Deployment Preparation (2 hours)
**Objective**: Prepare for deployment

**Tasks:**
- Create deployment documentation
- Set up configuration management
- Add logging and monitoring
- Create user documentation

---

## Key Changes from Original Plan

### 1. **Component-Driven Architecture**
- Focused on the 4 main components from specification
- Board Navigation, Controls, Buffer Board, Work Items Panel

### 2. **Specification Alignment**
- Header rows configuration (Cell Zones, Variance, Index, etc.)
- Time controls with real-time clock and Fast Forward
- CCR Status Component with health indicators

### 3. **Backend Integration Focus**
- All APIs are complete and tested
- Focus on frontend consuming existing secure APIs
- No need for backend development during frontend phases

### 4. **Realistic Timeline**
- 9 days total (Days 15-23)
- Accounts for complexity of buffer board visualization
- Includes comprehensive testing and integration

### 5. **TDD Maintained**
- Every component starts with failing tests
- Integration tests for complete workflows
- Performance and error handling validation

This updated plan leverages the completed backend and aligns with the detailed Buffer Board Components specification while maintaining the TDD approach throughout.

---

## Phase 9: Production Hardening & Advanced Features (Post-MVP)

### Day 9A: Email Integration & User Self-Service (Est. 2-3 Days)

#### Step 9.1: Email Service Integration
**Objective**: Integrate a transactional email service (e.g., SendGrid, Mailgun) into the backend.
- **Tasks**:
  - Configure email service provider.
  - Create an email sending utility in the backend.
  - Add API endpoints for sending templated emails.

#### Step 9.2: User Invitation Flow
**Objective**: Replace the manual user creation with a secure, email-based invitation system.
- **Tasks**:
  - Generate secure, single-use invitation tokens.
  - Create an "Invite User" email template.
  - Build a public-facing page for new users to accept invites and set their password.
  - Update the Org Admin UI to send email invitations.

#### Step 9.3: Password Reset Flow
**Objective**: Implement a self-service password reset feature.
- **Tasks**:
  - Create a "Forgot Password" feature on the login screen.
  - Generate secure password reset tokens.
  - Create a password reset email template.
  - Build a public-facing page for users to set a new password.
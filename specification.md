## Executive Summary

This specification defines a digital DBR (Drum Buffer Rope) buffer management system based on Theory of Constraints (TOC) principles. The system provides visual workflow management around Capacity Constrained Resources (CCR) to optimize flow and prevent resource starvation or overload.

## Core Concepts

### Buffer Management Definition
Buffer management is a TOC solution category used to make priorities clear within an environment of dependencies and variation. It helps answer: "How can people know what to do next, without managers interfering?"

### Key Problem Solved
In typical systems, "losses accumulate and gains get lost." DBR provides a visual display of accumulated losses and gains of all jobs in the buffer, preserving both positive and negative performance visibility.

### Flow Direction
Work items flow **right to left** through the system, mirroring the passage of time.

### DBR Board visulisation

![Pictures of BDR buffer boards from TOCICO Conference](<images/2025-07-15 mult-ccr buffer board.svg>)

---

## System Entities and Data Models
The following sections define the core data structures (schemas) of the DBR system as implemented in the `DBR_OpenAPI_Specification.yml`.

### 1. Organization
The `Organization` is the top-level entity representing a tenant in the multi-tenant system. All other data is scoped within an organization.

| Attribute | Type | Description |
|---|---|---|
| `id` | string (uuid) | Unique ID of the organization. |
| `name` | string | Name of the organization. |
| `description` | string | Detailed description of the organization. |
| `status` | enum | Current status: `active`, `suspended`, `archived`. |
| `contact_email`| string (email) | Primary contact email. |
| `country` | string | Country where the organization is based. |
| `subscription_level` | string | Subscription tier or feature access level. |
| `created_date` | string (date-time)| Date the organization was created. |
| `default_board_id` | string | The ID of the default DBR board for this organization. |

### 2. User
Represents an application user who can be a member of one or more organizations.

| Attribute | Type | Description |
|---|---|---|
| `id` | string (uuid) | Unique ID of the user. |
| `username` | string | Unique username for login. |
| `email` | string (email) | User's email address. |
| `display_name` | string | User's preferred display name. |
| `active_status`| boolean | Whether the user account is active. |
| `last_login_date`| string (date-time)| Date of the user's last login. |
| `created_date` | string (date-time)| Date the user account was created. |
| `system_role_id`| string (uuid) | ID of the system-wide role (e.g., "Super Admin"). |

### 3. Role
Defines a set of permissions within the system. Roles are system-defined.

| Attribute | Type | Description |
|---|---|---|
| `id` | string (uuid) | Unique ID of the role. |
| `name` | enum | Name of the role: `Super Admin`, `Organization Admin`, `Planner`, `Worker`, `Viewer`. |
| `description` | string | Description of the role's responsibilities. |

### 4. OrganizationMembership
This entity links a `User` to an `Organization` and assigns them a specific `Role` within that organization.

| Attribute | Type | Description |
|---|---|---|
| `id` | string (uuid) | Unique ID of the membership. |
| `organization_id`| string (uuid) | ID of the organization. |
| `user_id` | string (uuid) | ID of the user. |
| `role_id` | string (uuid) | ID of the role assigned to the user. |
| `invitation_status`| enum | Status of the invitation: `pending`, `accepted`, `declined`. |
| `invited_by_user_id`| string (uuid) | ID of the user who sent the invitation. |
| `joined_date` | string (date-time)| Date the user joined the organization. |

### 5. Collection (Project/MOVE)
A `Collection` is a container for a group of related `WorkItems`, such as a project, epic, or release.

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique ID of the collection. |
| `organization_id`| string (uuid) | ID of the parent organization. |
| `name` | string | Name of the collection. |
| `description` | string | Detailed description. |
| `type` | enum | Type of collection: `Project`, `MOVE`, `Epic`, `Release`. |
| `status` | enum | Current status: `planning`, `active`, `on-hold`, `completed`. |
| `owner_user_id`| string | ID of the user owning the collection. |
| `target_completion_date`| string (date-time)| Target completion date for the collection. |
| `target_completion_date_timezone`| string | IANA Time Zone for the target date. |
| `estimated_sales_price`| number | Revenue potential of the collection. |
| `estimated_variable_cost`| number | Material/variable costs for the collection. |
| `url` | string | Link to an external resource. |

### 6. WorkItem
The fundamental unit of work that flows through the DBR system.

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique ID of the work item. |
| `organization_id`| string (uuid) | ID of the parent organization. |
| `collection_id`| string | ID of the associated collection. |
| `title` | string | Brief, descriptive name of the work item. |
| `description` | string | Detailed specification of the work. |
| `due_date` | string (date-time)| Target completion date. |
| `due_date_timezone`| string | IANA Time Zone for the due date. |
| `status` | enum | Current status: `Backlog`, `Ready`, `Standby`, `In-Progress`, `Done`. |
| `priority` | enum | Priority level: `low`, `medium`, `high`, `critical`. |
| `estimated_total_hours`| number | Estimated total hours required. |
| `ccr_hours_required`| object | JSON object specifying hours required from different CCRs. |
| `estimated_sales_price`| number | Revenue potential of the work item. |
| `estimated_variable_cost`| number | Material/variable costs per work item. |
| `tasks` | array | A list of sub-tasks within the work item. |

### 7. Schedule
A time unit-sized bundle of `WorkItems` that moves across the DBR board.

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique ID of the schedule. |
| `organization_id`| string (uuid) | ID of the parent organization. |
| `board_config_id`| string | ID of the DBR board this schedule belongs to. |
| `capability_channel_id`| string | ID of the capability channel (CCR) this schedule is for. |
| `status` | enum | Current status: `Planning`, `Pre-Constraint`, `Post-Constraint`, `Completed`. |
| `work_item_ids`| array | Ordered list of Work Item IDs included in the schedule. |
| `total_ccr_hours`| number | The sum of CCR hours for all work items in the schedule. |
| `time_unit_position`| integer | The schedule's current position on the board relative to the CCR. |
| `created_date` | string (date-time)| When the schedule was created. |
| `released_date`| string (date-time)| When the schedule was moved to the pre-constraint buffer. |
| `completed_date`| string (date-time)| When the schedule was marked as complete. |

### 8. CCR (Capacity Constrained Resource)
A dedicated entity representing a resource that constrains the system's flow.

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique ID of the CCR. |
| `organization_id`| string (uuid) | ID of the parent organization. |
| `name` | string | Name of the CCR (e.g., "Senior Developers"). |
| `description` | string | Detailed description of the resource. |
| `capacity_per_time_unit`| number | The total available work hours for this CCR in a single time unit. |
| `time_unit` | enum | The unit of time used for capacity planning: `hours`, `days`, `weeks`. |

### 9. DBRBoardConfig
Stores the configuration for a specific DBR board, including its buffer sizes and layout.

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique ID of the board configuration. |
| `organization_id`| string (uuid) | ID of the parent organization. |
| `name` | string | Name of the DBR board. |
| `time_unit` | enum | The unit of time for the board: `hours`, `days`, `weeks`. |
| `pre_constraint_buffer_size`| integer | Number of time units in the pre-constraint (right) buffer. |
| `post_constraint_buffer_size`| integer | Number of time units in the post-constraint (left) buffer. |
| `is_paused` | boolean | Whether the automatic time progression is currently paused. |

---
## Work Item Data Structure

### Core Attributes
- **Unique ID:** Sequential identifier (e.g., "WI-0001")
- **Title:** Brief descriptive name
- **Description:** Detailed work item specification
- **Due Date:** Target completion date
- **Status:** Visual symbol/indicator with flow impact clarity

### Status Management
**Purpose:** Make flow issues immediately visible to prevent delays

**Status Categories:**
- **Progressive Completion:** Auto-calculated based on task completion percentage
- **Manual Overrides:** Human-set status when issues arise
- **Flow Impact Indicators:** Clear visual signals when work flow is at risk

**Status Requirements:**
- **Issue Visibility:** Make it very clear when there are issues that might impact work flow
- **Immediate Recognition:** Visual symbols/colors that instantly communicate problems
- **Flow Prevention:** Status should trigger appropriate team responses
- **Override Capability:** Allow manual status setting when auto-calculation insufficient

**Implementation Notes:**
- Status logic to be determined (manual for first release)
- Must integrate with Progressive Completion percentage
- Should trigger alerts/notifications for flow-impacting issues
- Visual design must make problems immediately obvious

### Resource Requirements
- **Resource List:** All required resources with time estimates
- **CCR Flagging:** One resource flagged as the Capacity Constrained Resource
- **Time per Resource:** Estimated time required for each resource

### Financial Attributes
- **Estimated Sales Price:** Revenue potential of work item
- **Estimated Variable Cost:** Material/variable costs per work item
- **Throughput Calculation:** Sales Price - Variable Costs
- **Throughput per Constraint Unit:** Throughput ÷ Time at CCR

### Task Management
- **Tasks/Todos:** Checklist of sub-items within work item
- **Mark-Off Capability:** Ability to tick off completed tasks
- **Progress Visualization:** % completion based on completed tasks
- **Task Creation:** Add new tasks to work items
- **Task Updates:** Modify existing tasks

### Ongoing Work Item Updates
**Continuous Activity:** Work item updating occurs throughout the time it spends in the buffer system.

**Update Process:**
1. **Task Completion:** People mark off individual tasks as work progresses
2. **Progress Tracking:** Running percentage of completed tasks
3. **Real-time Updates:** Task status updates happen continuously during work
4. **Work Item Completion:** When all tasks marked complete, entire work item declared Done/Complete
5. **Schedule Impact:** Work item completion contributes to overall schedule completion

**Buffer Activity:**
- **Not Static:** Schedules in buffer zones have active work happening
- **Continuous Progress:** Task completion happening across all buffer positions
- **Visual Updates:** Progress indicators update in real-time as work progresses
- **Completion Triggers:** Work item and schedule completion drives removal from board

### Communication & Tracking
- **Comments:** Timestamped comments/notes on work item
- **Comment History:** Full audit trail of all comments
- **Status Updates:** Track status changes over time

## Throughput Accounting

### Core Philosophy
Throughput accounting focuses on maximizing value passing through the system's bottleneck (CCR), fundamentally different from traditional cost accounting.

### Key Principles

#### Throughput Calculation
- **Formula:** Throughput = Sales Price - Direct Variable Costs (only)
- **Exclude:** Full manufacturing costs, labor costs, overhead allocations
- **Include:** Only truly variable costs that change with each work item

#### Constraint Focus
- **Maximize Value:** Focus on maximizing throughput at the constraint
- **Bottleneck Optimization:** All improvement efforts target the CCR
- **System Perspective:** Total system throughput limited by constraint throughput

#### Financial Metrics
- **Throughput per Work Item:** Sales Price - Variable Costs
- **Throughput per Constraint Unit:** Throughput ÷ Time at CCR
- **Total System Throughput:** Sum of all throughput passing through CCR

### Strategic Implications

#### Decision Making
- **Prioritization:** Rank work items by throughput per constraint unit (not profit margin)
- **Resource Allocation:** Maximize constraint utilization over cost minimization
- **Investment Focus:** Improve constraint capacity over non-constraint efficiency

#### Traditional vs. Throughput Accounting
- **Traditional:** Minimize cost per unit, maximize local efficiency
- **Throughput:** Maximize value through constraint, optimize global system
- **Traditional:** Focus on cost reduction everywhere
- **Throughput:** Focus improvement efforts only on constraint

### Implementation Benefits
- **Clear Prioritization:** Objective ranking of work items by financial impact
- **Resource Focus:** Concentrate efforts where they matter most
- **Profitability Growth:** Increase total system profitability through constraint optimization
- **Decision Clarity:** Financial framework for all flow management decisions

### Digital System Integration
- **Automatic Calculation:** System calculates throughput per constraint unit
- **Priority Ranking:** Auto-sort work items by throughput value
- **Financial Dashboard:** Display throughput metrics alongside flow metrics
- **Decision Support:** Provide throughput data for planning decisions

### 1. Backlog
- **Purpose:** Where new work items are created
- **Representation:** Piece of paper describing the work item
- **Flexibility:** Full flexibility to reorder work items

### 2. Ready (formerly "Full Kitted")
- **Purpose:** Ensure everything needed is available before starting work
- **TOC Concept:** Check off all requirements to complete work "in one setting"
- **Problem Solved:** Prevents work starting then pausing due to missing materials/information
- **Software Context:** Dependencies resolved, requirements clear, acceptance criteria defined
- **Flexibility:** Full flexibility to reorder work items

## Schedule Data Structure

### Definition
"The Schedule" is the core artifact assembled during Planning and moved through the buffer system. It represents one time unit's worth of work.

### Core Attributes
- **Unique ID:** Sequential identifier for tracking (e.g., "SCH-2025-001")
- **Created Date:** When schedule was assembled during Planning
- **Released Date:** DateTime when moved onto pre-constraint board
- **Completion Date:** DateTime when marked Done and moved off board
- **Time Unit Size:** The capacity limit for this schedule

### Work Item Management
- **Sequenced Work Items:** Ordered list of work items in priority sequence
- **CCR Time per Work Item:** Time required by CCR resource for each work item
- **Running Sum Display:** Real-time total of CCR time for all work items in schedule
- **Capacity Constraint:** Total CCR time cannot exceed time unit capacity
- **Resequencing:** Ability to move work items up/down in priority order during Planning

### Planning Process
1. **Start Empty Schedule:** Begin with zero CCR time
2. **Add Work Items:** Select from Ready work items following Planning Rules
3. **Track Capacity:** Monitor running sum of CCR time
4. **Capacity Check:** Cannot add work item if it would exceed time unit capacity
5. **Resequence:** Adjust priority order as needed
6. **Finalize:** Lock sequence when schedule moves to buffer zones

### Movement Tracking
- **Planning Stage:** Full flexibility to modify work items and sequence
- **Buffer Zones:** Locked - no modifications allowed
- **Left Movement:** Schedule moves one time slot left at each Standup
- **Completion:** Schedule removed when all work items completed

### Visual Representation
- **Physical Metaphor:** Paper clip holding work item pages
- **Cover Sheet:** Shows schedule ID, total CCR time, completion status
- **Work Item Pages:** Individual pages for each work item with checkboxes
- **Progress Indicator:** Visual percentage of completed work items

### Capacity Management
**Core Constraint:** Total CCR time ≤ Time Unit capacity

**Example:**
- Time Unit = 8 hours
- Work Item A = 3 hours CCR time
- Work Item B = 2 hours CCR time
- Work Item C = 2.5 hours CCR time
- Total = 7.5 hours (within 8-hour capacity)
- Cannot add Work Item D requiring 1+ hours
- **Purpose:** Assemble Ready work items into time unit-sized schedules
- **Input:** Only Ready work items (cannot schedule non-Ready items)
- **Process:** Follow agreed Planning Rules to select and sequence work items
- **Output:** Schedules (time unit bundles)
- **Physical Representation:** Paper clip holding work item pages together
- **Bundle Structure:**
  - Work item pages with checkboxes
  - Cover sheet showing at-a-glance status
  - Easy resequencing by moving pages in stack
- **Time Constraint:** Sum of work items ≤ time unit capacity
- **Special Cases:**
  - Zero work days: Bundle with cover page only (0 hours)
  - Multi-time unit work: Sequential pages across multiple bundles

### 4. Buffer Zones
- **Movement Rule:** NO reordering once schedules enter buffer zones
- **Committed Flow:** Sequence locked until completion

## Planning Rules

### Core Rule
1. **Plan in, what came out** - to avoid "buffer flooding"

### Example Planning Rules
- Pick Big, medium then small work items for each schedule
- Pink then green then blue work items
- MOVE A first, then MOVE B work items (MOVE = collection of work items from Tameflow)
- No more than 7 work items per schedule

### Hybrid Planning Approaches
DBR can be integrated with higher-level planning methodologies:

- **DBR + CCPM:** Use DBR for detailed work-item management while CCPM handles bigger picture project planning
- **DBR + Tameflow MOVE:** Use DBR for individual work items while Tameflow MOVE planning manages collections of related work items
- **Multi-Level Planning:** DBR operates at tactical level while strategic planning methods handle portfolio/program level
- **Dual DBR Boards:** Operate two DBR boards simultaneously:
  - **Operational DBR:** Work item level with fine-grained resolution (hours/days)
  - **Strategic DBR:** Portfolio/program level with coarse resolution (weeks/months)

## CCR (Capacity Constrained Resource)

### Definition
The one resource that limits flow through the entire system.

### Software Business Context
- **Flow Type:** Skill-based flow
- **Common CCRs:** Developer, Senior Developer, Security Expert, DevOps Engineer, UX Designer, Architect
- **Planning Focus:** All scheduling based on CCR availability
- **Supporting Resources:** Have surplus capacity to support CCR

### Position
- **Board Position:** CCR sits at position "0" - the central reference point
- **Measurement:** All time units measured relative to CCR position

## Buffer Zone System

### Pre-Constraint Zones (Right of CCR)
**Purpose:** Ensure CCR never runs out of work

- **Zone 1 (Green):** Safe - adequate work buffer
- **Zone 2 (Yellow):** Warning - starting to run low on work
- **Zone 3 (Red):** Alarm - very close to running out (3 time units away)

### Post-Constraint Zones (Left of CCR)
**Purpose:** Monitor and respond to work taking longer than planned

- **Zone 3 (Green):** Normal - work taking slightly longer (expected variation)
- **Zone 2 (Yellow):** Concern - work significantly behind, action needed
- **Zone 1 (Red):** Critical - immediate intervention required
- **Zone 0 (Black):** Catchall - work taking well beyond expected variation

## Time Unit System

### Flexible Time Units
- **Variable Resolution:** Different DBR boards can use different time unit sizes
- **Examples:** Hours, days, weeks
- **Matching Principle:** Time unit should match work type characteristics
- **Multiple Boards:** Organization can run parallel DBR boards with different time units

### Buffer Sizing

#### Initial Buffer Sizing Formula
When implementing DBR, size the overall buffer as the **greater of:**
- **Half the current average work-item flow time**
- **Double the current work-item expedite time**

Then split this overall buffer into Pre-Constraint and Post-Constraint portions.

#### Buffer Sizing Principles
- **Independent Sizing:** Pre-constraint and post-constraint buffers can be different sizes
- **Customizable Parameters:** Buffer sizes tunable based on work characteristics
- **Example:** Pre-constraint 9 time units, Post-constraint 3 time units
- **Behavioral Engineering:** Buffer sizing drives team behavior and focus

#### Key Implementation Insights
- **Time Units Enable Visibility:** Splitting buffers into time units makes "work on the move" visible
- **Iterative Improvement:** Start with initial sizing, tune through working with the board
- **No Perfect Start:** Don't need correct buffer sizes initially - improve through usage
- **Minimal Buffer Variety:** Organization doesn't need many different buffers
- **Buffer Relationship:** If multiple buffers needed, make them double or half size of main buffer (significantly different)
- **Variation Absorption:** Buffers naturally absorb work variation, reducing need for multiple buffer types

#### Tuning Philosophy
**Key Insight:** Only by working with the DBR board and improving do you tune the board for your specific work-item characteristics. The system teaches you the right sizing through usage.

## Visual Indicators

### Numerical Scale
- **Scale:** -6, -5, -4, -3, -2, -1, CCR, +1, +2, +3, +4, +5, +6
- **Purpose:** Show how many time units ahead or behind schedule
- **Visual Management:**
  - Shorter row = ahead of schedule
  - Longer row = behind schedule
  - Row length directly indicates schedule variance

## Operational Procedures

### The Standup Meeting
**Frequency:** Every time unit

**Activities (in order):**
1. **Review:** All schedules across buffer zones
2. **Remove:** Completed schedules from board
3. **Move Left:** All remaining schedules shift one time slot left
4. **Release:** Next planned schedule into now-free slot on right

**Key Principle:** TIME NEVER STOPS - board replicates this reality

### Operational Procedures & API Mapping
The conceptual operations of the DBR system are implemented through a RESTful API. The standup meeting, which occurs every time unit, is driven by specific API calls:

1.  **Review:** The team reviews all schedules on the board. This is a visual action supported by `GET /schedules` and `GET /board_configs/{configId}`.
2.  **Remove Completed:** Completed schedules are removed from the board via `DELETE /schedules/{scheduleId}`.
3.  **Move Left:** All remaining schedules are shifted one time slot to the left. This core DBR mechanic is triggered by a single API call: `POST /system/advance_time_unit`.
4.  **Release:** The next planned schedule is released from planning into the now-free slot on the right side of the board. This is achieved by updating a schedule's status via `PUT /schedules/{scheduleId}`.

### System Control Operations
The API provides endpoints for controlling the DBR board's timer, which is critical for facilitating meetings and handling exceptions.

*   **Pause Board:** To halt the automatic time progression (e.g., during a stand-up), a `POST /board_configs/{configId}/pause` request is made.
*   **Unpause Board:** To resume the timer, a `POST /board_configs/{configId}/unpause` request is made. The system will automatically catch up on any time units that passed during the pause.

### Schedule Movement Rules
- **When Ahead:** Work completed faster than planned, row becomes shorter
- **When Behind:** Work takes longer, schedules stay on board, row becomes longer
- **Automatic Tracking:** Daily left-shift creates automatic schedule variance tracking

## Multi-Team Implementation

### Stacked Buffer Structure
- **Multiple Rows:** Each row represents one complete DBR buffer system
- **Row Assignments:** Different workstream, team, person, or CCR
- **Benefits:**
  - At-a-glance visibility across all teams
  - Comparative analysis of team performance
  - Resource allocation decisions
  - Portfolio-level flow management

### Dependency Management
- **Minimize Dependencies:** Key design principle between rows
- **Prioritization Rules:** Clear rules about CCR/Row priority
- **Resource Mobility:** Quick resource movement to rows needing help

## Buffer Log

### Data Capture
- **Timing:** Every time unit after board updates
- **Data:** All buffer over/under counts for each CCR/row
- **Purpose:** Historical analysis and trend identification

### Analysis Capabilities
- Trend analysis over time
- Performance comparison between CCRs/teams
- Predictive insights and early warning patterns
- Data-driven buffer size optimization
- Retrospective problem analysis

## UI Design Features Analysis

### Image 1 - Detailed Task Management View

**Key Design Features:**
- **Person-based columns** - Individual swim lanes for each team member
- **Time allocation display** - "Idle for X hours/minutes" shows capacity utilization
- **Hierarchical work organization** - Projects (PAVE, BRIT, WTG) containing multiple work items
- **Work item details** - Full task descriptions visible within buffer zones
- **Individual work item IDs** - Unique identifiers (WW00043978, etc.) prominently displayed
- **Release Capacity section** - Separate area showing workload distribution
- **Buffer penetration percentages** - Numerical indicators (91.7%, 83.3%) showing buffer utilization
- **Color-coded project groupings** - Visual differentiation of project types
- **Task status indicators** - Various symbols and colors indicating work item states
- **Detailed work descriptions** - Full text of what each work item entails
- **Time tracking integration** - Shows how long people have been idle/working

### Image 2 - Resource Capability Buffer View

**Key Design Features:**
- **Resource capability channels** - Vertical swim lanes by skill type (Blue, Cyan, Green, Magenta)
- **Task cards as tokens** - Individual moveable pieces representing work items
- **Age percentile indicators** - Horizontal scale showing time progression (11.1%, 16.7%, etc.)
- **Clear zone demarcation** - Visual separation of Pre-CCR, CCR Line, Post-CCR zones
- **Task identification within tokens** - Labels like "F3 Task", "F9 Task" on individual pieces
- **Grid-based layout** - Clear cell structure for precise positioning
- **Buffer zone percentage markers** - Top row showing completion percentages
- **Color gradient zones** - Smooth transition from blue (safe) to red (critical)
- **Token density visualization** - Can see work concentration in different zones
- **Capability-based grouping** - Work organized by required skill sets

### Design Features Inventory

#### MVP Features (Priority 1)
- Multi-row CCR layout
- Basic buffer zone color coding (red/yellow/green)
- Work item representation as moveable blocks
- Time slot headers with numerical indicators
- Basic status text for each CCR row
- Add/remove work items functionality
- Simple drag-and-drop between zones

#### Enhanced Features (Priority 2)
- Person/resource-based swim lanes
- Work item detail panels with full descriptions
- Progress percentage indicators
- Project grouping and color coding
- Individual work item IDs prominently displayed
- Time allocation and capacity utilization display
- Buffer penetration percentage calculations

#### Advanced Features (Priority 3)
- Age/time progression indicators
- Resource capability channels
- Task tokenization with detailed labels
- Hierarchical work organization (projects → work items)
- Real-time capacity tracking ("Idle for X hours")
- Advanced status indicators and symbols
- Grid-based precise positioning
- Release capacity management section

### UI Controls Analysis (Image 1)

**Top Right Control Panel Features:**
- **Search/Filter** - Find specific work items, people, or projects
- **Pause button + Clock** - Likely pauses time progression or shows countdown to next time unit
- **Configuration button** - System settings, buffer sizing, rules configuration
- **Refresh button** - Manual update/sync of current state
- **"People or Teams" button** - Toggle between individual vs. team views
- **Globe icon** - Possibly multi-site/location management or timezone settings
- **Column/Row controls** - Likely toggles view orientation or grouping modes

**Time Management Controls:**
- **Clock with countdown** - Shows time remaining until next standup/time unit progression
- **Pause functionality** - Ability to halt automatic time progression for planning/analysis
- **Manual progression** - Button-triggered movement rather than drag-and-drop

### Interaction Model Reconsideration

**Button-Based Operations vs. Drag-and-Drop:**

#### Time Progression (Core Operation)
- **Automatic:** System moves all schedules left at defined intervals
- **Manual Trigger:** "Next Time Unit" button for controlled progression
- **Pause/Resume:** Ability to halt time progression for planning activities

#### Work Item Management
- **Add to Planning:** Button-based addition from Ready → Planning
- **Mark Complete:** Button/checkbox to mark schedules as Done
- **Resequencing:** Within Planning only - before schedules enter buffer zones

#### Standup Meeting Controls
- **Review Mode:** Special interface for daily standup meetings
- **Bulk Operations:** Mark multiple schedules complete simultaneously
- **Time Unit Advance:** Single button to trigger left-shift of all remaining schedules

#### Administrative Controls
- **Search/Filter:** Find specific work items across all zones
- **View Toggles:** Switch between board views (people vs. teams vs. projects)
- **Configuration:** Adjust buffer sizes, time units, rules
- **Refresh/Sync:** Update real-time data

### MVP Interaction Model

**Primary Operations:**
1. **Time Progression Button** - Core operation that moves everything left
2. **Add to Planning** - Move work items from Ready to Planning queue
3. **Mark Complete** - Remove finished schedules from board
4. **Search/Filter** - Find specific work items quickly

**Secondary Operations:**
5. **Pause/Resume** - Control automatic time progression
6. **View Toggles** - Switch between different board layouts
7. **Configuration** - Adjust system parameters

**Drag-and-Drop Limitations:**
- Only within Planning zone (before schedules lock into buffer)
- Once in buffer zones, schedules move only via time progression
- Maintains the "time never stops" principle
- Prevents gaming the system through manual repositioning

### Buffer Board Components

Main DBR Buffer Board Interface structure with the four key components you identified. Each component now has detailed sub-elements defined.

#### Controls Component:

Time progression as primary operation (not drag-and-drop)
Standup meeting optimization
View management and configuration options

#### Buffer Boards Component:

- Visual buffer zone representation
- Multi-CCR row display
- Interactive schedule and work item access

##### Detailed Buffer board features

* Consists of multiple rows of cells which we can call a "Capability Channel"
* The "Capability Channel" is in turn broken down into cells based on the buffer Zone configuration.
* Each Cell has an indicator with a count of the number of incomplete Work-Items for the schedule that is currently allocated to that cell of the "Capability Channel"
* By default the cell displays an overview of the highest incomplete Work Item in the allocated schedule.
  - The work-item overview should display Work Item Number, Title, The count of work item tasks done and incomplete and work item status indicators.
  - The "Cell WI count indicator" also servers a a navigation tool to display a list of the work items in the schedule. By navigating the list one can select the WI summary to display in the cell.
  - It is possible to open up a panel or navigate to the work item displayed in the cell
    + Via the work "item panel" it possible to edit the work item task status and add comments to the work item.

* On the left hand side of the "Capability Channel"  there is a narrow column with key CCR status information.
  - CCR should ideally be kept working all the time. The hight of the CCR Status bar represents the elapsed time of the "Unit of Time". The CCR will "Check in/out" to work on the work-item.  A vertical "hour glass view" of call background colour in red and green indicates how much of the time is spent working on a work item or not.

* There can be only one Schedule per cell.
* The background of the cell is coloured based on the configuration for a given Zone that the cell is in.  Buffer Board Navigation Controls
* Vertical and horizontal navigation sliders enables user to slide view left/right and up/down if required
* Zoom in Out and reset view of the cells

#### Standby Work Items Component:

- Planning queue management
- Integration with Planning interface
- Priority and dependency visualization

#### CCR Status Component:

- Real-time health indicators
- Performance metrics
- Alert and notification integration


## User Roles and Organizational Structure

### Multi-Tenant Architecture
The system is designed as a multi-tenant application.
- **Organizational Isolation:** All data is strictly partitioned by `organization_id`. API requests must specify the organization to ensure users can only access data they have permission for.
- **Data Separation:** Complete data isolation between organizations is enforced at the API and database level.

### User Role Hierarchy
The system defines five roles, as specified in the **Role** entity table above. The responsibilities for each role are outlined below.

#### Application Administrator (Super Admin)
- **Purpose:** Manages the entire application across all organizations.
- **API Access:** Can create and manage `Organization` entities. Can assign the `Organization Admin` role to users.

#### Organization Administrator
- **Purpose:** Manages the DBR system within their specific organization.
- **API Access:** Full CRUD access to users, roles, CCRs, and board configurations within their `organization_id`.

#### Planner
- **Purpose:** Creates and manages schedules for assigned CCRs.
- **API Access:** Can create and update `Schedule` entities. Can read `WorkItem` entities to plan them into schedules.

#### Worker
- **Purpose:** Updates work progress and task completion.
- **API Access:** Can update the status of `WorkItem` tasks and add comments.

#### Viewer
- **Purpose:** View DBR boards and reports without modification rights.
- **API Access:** Read-only (`GET`) access to most entities within their organization.

### Organizational Data Structure

#### Organization Attributes
- **Organization ID:** Unique identifier
- **Organization Name:** Display name
- **Organization Description:** Purpose and context
- **Created Date:** When organization was established
- **Status:** Active, suspended, archived
- **Contact Information:** Primary contact details
- **Subscription Level:** Feature access level (if applicable)
- **Data Retention Policy:** How long to keep historical data

#### Organization Settings
- **Default Time Units:** Standard time unit configurations
- **Default Buffer Sizes:** Standard pre/post constraint buffer sizes
- **Planning Rules Templates:** Common rule sets for the organization
- **Notification Settings:** Organization-wide notification preferences
- **Integration Configurations:** External system connections
- **Branding Settings:** Organization logo, colors, terminology

### User Management Within Organizations

#### User Attributes (Organization-Scoped)
- **User ID:** Unique within organization
- **Username/Email:** Login credentials
- **Display Name:** Full name for interface
- **Role Assignments:** Which roles user has within organization
- **CCR Assignments:** Which CCRs user can plan for (if Planner role)
- **Department/Team:** Organizational context
- **Contact Information:** Phone, email, location
- **Active Status:** Active, inactive, suspended
- **Last Login:** Track user activity

#### Cross-Organization User Access
- **Multi-Organization Users:** Users can belong to multiple organizations
- **Organization Context:** Clear indication of which organization user is working in
- **Context Switching:** Ability to switch between organizations (if permissions allow)
- **Separate Permissions:** Different roles in different organizations

### Administrative Interfaces

#### Application Administrator Interface
- **Organization Dashboard:** Overview of all organizations
- **Global User Management:** Cross-organization user administration
- **System Settings:** Application-wide configuration
- **Usage Analytics:** Cross-organization usage and performance metrics
- **Security Management:** Global security policies and audit logs

#### Organization Administrator Interface
- **User Management Dashboard:** Manage organization users and roles
- **CCR Configuration:** Set up resources and constraint definitions
- **DBR Board Setup:** Configure buffer boards and time units
- **Rules Management:** Define and manage Planning Rules
- **Organization Settings:** Configure organization-specific preferences
- **Analytics Dashboard:** Organization-specific reports and metrics

### Security Framework

#### Authentication
- **Organization-Scoped Login:** Users authenticate within organizational context
- **Authentication Methods:**
  - Username/password
  - Single Sign-On (SSO) per organization
  - Third-party providers (Google, Microsoft, LDAP)
- **Multi-Factor Authentication:** Enhanced security for administrative roles
- **Session Management:** Secure session handling with appropriate timeouts

#### Authorization and Access Control
- **Role-Based Access Control (RBAC):** Permissions based on assigned roles
- **Resource-Level Permissions:** Fine-grained access to specific CCRs, projects
- **Organization Boundaries:** Strict enforcement of organizational data isolation
- **Audit Logging:** Complete audit trail of all administrative actions

#### Data Security
- **Encryption:** Data encrypted in transit and at rest
- **Access Logging:** All data access logged for audit purposes
- **Data Retention:** Configurable data retention policies per organization
- **Backup Security:** Secure backup and recovery procedures

### Application-Wide Configuration

#### Global System Settings
- **Time Unit Options:** Available time unit types (hours, days, weeks)
- **Buffer Zone Colors:** Standard color schemes for buffer zones
- **Default Planning Rules:** Template rule sets for new organizations
- **Notification Templates:** Standard notification formats and timing
- **Report Templates:** Standard report formats and metrics

### Main DBR Buffer Board Interface Requirements

### Interface Component Overview
The Main DBR Buffer Board Interface is the central hub where daily standup meetings occur and real-time flow visualization takes place. It consists of four primary components:

1. **Controls** - User interface controls for board operations
2. **Buffer Boards** - Visual representation of the buffer zones and schedules
3. **Standby Work Items** - Work items ready for planning but not yet scheduled
4. **CCR Status** - Current status and health indicators for each CCR


### Component 1: Controls

#### Time Progression Controls
- **Next Time Unit Button** - Primary control to advance all schedules one time slot left
- **Pause/Resume Time** - Control automatic time progression
- **Time Unit Clock** - Display countdown to next automatic progression
- **Manual Override** - Force immediate time progression when needed

#### View Management Controls
- **Search/Filter** - Find specific work items, schedules, or CCRs across the board
- **View Toggles** - Switch between different board layouts (people vs. teams vs. projects)
- **Zoom Controls** - Adjust board detail level and density
- **Refresh/Sync** - Manual update of real-time data

#### Board Configuration Controls
- **CCR Selection** - Show/hide specific CCR rows
- **Time Horizon** - Adjust visible time slot range
- **Buffer Zone Display** - Toggle zone colors and indicators
- **Layout Options** - Adjust board orientation and spacing

#### Standup Meeting Controls
- **Standup Mode** - Special interface optimized for daily standup meetings
- **Review Controls** - Step through each CCR row systematically
- **Bulk Complete** - Mark multiple schedules as complete simultaneously
- **Meeting Timer** - Track standup meeting duration

### Component 2: Buffer Boards

#### Buffer Zone Visualization
- **Time Slot Headers** - Numerical indicators showing time units relative to CCR
- **Zone Color Coding** - Visual representation of buffer zones (red/yellow/green)
- **CCR Position Marker** - Clear indication of constraint position (time unit 0)
- **Buffer Penetration Indicators** - Visual alerts when zones are penetrated

#### Schedule Representation
- **Schedule Blocks** - Visual representation of schedules in time slots
- **Schedule Details** - Hover/click to see schedule contents
- **Progress Indicators** - Visual progress bars showing schedule completion
- **Schedule IDs** - Clear identification of each schedule

#### Multi-CCR Display
- **CCR Row Labels** - Clear identification of each constraint resource
- **Row-Specific Controls** - Controls specific to each CCR row
- **Cross-CCR Dependencies** - Visual indicators of dependencies between rows
- **Row Status Indicators** - Health status for each CCR row

#### Interactive Features
- **Schedule Detail View** - Expand schedule to see contained work items
- **Work Item Details** - Access individual work item information
- **Progress Updates** - Quick progress marking capabilities
- **Comments/Notes** - Add notes to schedules or work items

#### Buffer Board Navigation Control
- **Board Scrolling** - Horizontal scroll to view extended time horizons
- **Zoom Controls** - Adjust time slot width and detail level
- **Time Range Selection** - Jump to specific time periods or buffer zones
- **Full Board View** - Overview mode showing entire buffer system
- **Focus Mode** - Concentrate on specific CCR rows# DBR Buffer Management System - Requirements Specification

### Component 3: Standby Work Items

#### Planning Queue Display
- **Ready Work Items** - List of work items available for planning
- **Project Grouping** - Organize work items by project/MOVE
- **Priority Indicators** - Visual priority levels for work items
- **Dependency Status** - Show dependency resolution status

#### Work Item Information
- **Work Item Summary** - Key information for each standby work item
- **CCR Requirements** - Time required from each constraint resource
- **Throughput Indicators** - Throughput per constraint unit values
- **Due Date Indicators** - Visual alerts for approaching due dates

#### Planning Integration
- **Add to Planning** - Quick controls to move items to Planning interface
- **Bulk Selection** - Select multiple work items for planning
- **Filter Options** - Filter standby items by various criteria
- **Sort Options** - Sort by priority, due date, throughput value

### Component 4: CCR Status

#### Real-Time Status Indicators
- **Buffer Health** - Current buffer zone status for each CCR
- **Schedule Variance** - How many time units ahead or behind schedule
- **Workload Indicators** - Current work distribution and capacity utilization
- **Alert Status** - Any active alerts or warnings for the CCR

#### Performance Metrics
- **Throughput Tracking** - Current and historical throughput values
- **Buffer Penetration History** - Recent buffer zone performance
- **Schedule Completion Rate** - Percentage of schedules completed on time
- **Capacity Utilization** - How effectively CCR capacity is being used

#### Action Items
- **Planning Alerts** - Notifications when planning action required
- **Escalation Indicators** - Visual alerts for issues requiring attention
- **Resource Availability** - Current status of CCR team members
- **Upcoming Commitments** - Preview of scheduled work

#### Communication Integration
- **Team Notifications** - Alerts and messages for CCR teams
- **Planner Alerts** - Notifications for designated planners
- **Escalation Messages** - Automatic escalation when buffers penetrate critical zones
- **Status Updates** - Real-time status broadcasting to relevant stakeholders

## Core Design Considerations

### 1. Platform Support

#### Web Browser UI
- **Primary Interface:** Feature-rich web application for desktop and laptop devices
- **Browser Compatibility:** Modern browsers (Chrome, Firefox, Safari, Edge)
- **Screen Optimization:** Designed for larger screens with complex data visualization
- **Keyboard Navigation:** Full keyboard accessibility for power users

#### Mobile UI
- **Secondary Interface:** Responsive web app optimized for smartphones and tablets
- **Touch Optimization:** Touch-friendly interface elements and gestures
- **Essential Functions:** Focus on core operations (view, update progress, mark complete)
- **Offline Capability:** Consider offline viewing of recently accessed work items

### 2. User Authentication

#### Authentication Requirements
- **Mandatory Authentication:** All users must authenticate to access the system
- **Authentication Methods:**
  - Username/password
  - Single Sign-On (SSO)
  - Third-party providers (Google, Microsoft, LDAP)
- **User Identity:** System uniquely identifies each user for personalization and audit trails
- **Session Management:** Secure session handling with appropriate timeouts

#### User Account Management
- **User Profiles:** Basic user information and preferences
- **Role Assignment:** Future capability for role-based access control
- **Audit Trail:** All user actions tracked with timestamps and user identification

### 3. Default View: Recently Viewed/Edited Work Items

#### Personalized Dashboard
- **Purpose:** Improve productivity by providing quick access to most relevant work items
- **User-Specific:** Each user sees their own recently accessed items
- **Smart Ordering:** Combination of recently viewed and recently edited, with recent edits prioritized

#### Implementation Requirements
- **Metadata Tracking:** Record last viewed and last edited timestamps per user per work item
- **Performance:** Fast loading of personalized dashboard
- **Configurable:** Users can adjust number of recent items displayed
- **Fallback:** If no recent items, show relevant work items based on assignments

#### Data Model Example
```
User_WorkItem_Activity:
- Work Item ID
- User ID
- Last Viewed Timestamp
- Last Edited Timestamp
- View Count
- Edit Count
```

### 4. Work Item List Actions

#### Primary Actions
- **View Action:** Clear and accessible "View" button/link for each work item
- **Quick Edit:** Inline editing capability for basic fields
- **Status Update:** Quick status change without opening full detail view
- **Progress Update:** Mark tasks complete directly from list view

#### Secondary Actions
- **Clone:** Duplicate work item for similar tasks
- **Move to Project:** Change project/MOVE association
- **Add Dependencies:** Quick dependency linking
- **Delete:** Remove work item (with confirmation)

#### Bulk Actions
- **Multi-Select:** Checkbox selection for bulk operations
- **Bulk Status Update:** Change status for multiple items
- **Bulk Assignment:** Assign multiple items to team members
- **Bulk Project Move:** Transfer multiple items between projects

### 5. Work Item Detail View

#### Comprehensive Information Display
- **All Attributes:** Complete work item information in organized sections
- **Related Items:** Dependencies, dependents, project context
- **Activity History:** Audit log of all changes with timestamps and users
- **Comments:** Threaded discussion and notes

#### Editing Capabilities
- **Inline Editing:** Quick updates for individual fields
- **Form Mode:** Full editing mode for comprehensive changes
- **Auto-Save:** Periodic saving of changes to prevent data loss
- **Change Validation:** Real-time validation of business rules

#### Interactive Features
- **Task Management:** Add, edit, complete tasks within work item
- **Dependency Management:** Visual dependency editor
- **File Attachments:** Support for relevant documents and images
- **Time Tracking:** Integration with time logging if required

## Planning Interface Requirements

### Core Purpose
The Planning interface is where Ready work items are assembled into time unit-sized schedules following agreed Planning Rules. This is the critical transition point from flexible work item management to committed, time-locked schedules.

### Planning Authority and Access Control

#### CCR-Specific Planning Authority
- **Designated Planners:** Each CCR row has one or more designated planners
- **Planning Permissions:** Only authorized planners can create schedules for their assigned CCR
- **Planner Assignment:** System tracks which users are authorized planners for each CCR
- **Cross-CCR Restrictions:** Planners cannot create schedules for CCRs they're not authorized for

#### Planner Management
- **Planner Assignment Interface:** Admin function to assign planners to CCRs
- **Backup Planners:** Support for multiple planners per CCR for coverage
- **Planner Notifications:** Automated alerts when planning action required
- **Planning Dashboard:** Planner-specific view showing all CCRs they manage

### Resource and CCR Management

#### Resource Definition System
- **Resource Registry:** Centralized list of all available resources (people, skills, equipment)
- **Resource Attributes:** Name, contact details, owner, capacity, skills
- **Resource Availability:** Track working hours, time off, capacity per time unit
- **Resource Relationships:** Team structures and skill hierarchies

#### CCR Configuration
- **CCR Designation:** Resources become CCRs when assigned to DBR rows
- **Multi-Resource CCRs:** Support for teams as CCRs (e.g., 2 developers = 1 CCR)
- **Capacity Calculation:** CCR capacity = number of resources × hours per time unit × time unit
- **Example:** 2 developers × 7 hours/day × 1 day = 14 hours CCR capacity
- **Capacity Override:** Allow manual adjustment of calculated capacity

#### Team-Based CCR Management
- **Team Composition:** Define which resources comprise a CCR team
- **Shared Capacity:** Calculate total CCR capacity across team members
- **Resource Substitution:** Handle when team members are unavailable
- **Skill Equivalency:** Define which resources can substitute for others

### Alerting and Notification System

#### Buffer Status Monitoring
- **Zone Penetration Alerts:** Automatic notifications when pre-constraint buffer enters yellow/red zones
- **Capacity Alerts:** Warnings when CCR approaching work starvation
- **Threshold Configuration:** Customizable alert thresholds per CCR
- **Escalation Rules:** Progressive alerts as buffer situation worsens

#### Notification Delivery
- **Email Notifications:** Send alerts to designated planners
- **In-App Notifications:** Dashboard alerts and status indicators
- **SMS/Mobile Alerts:** Critical alerts via mobile for urgent situations
- **Integration Options:** Slack, Teams, or other messaging platform integration

#### Alert Types
- **Planning Required:** Pre-constraint buffer needs refilling
- **Capacity Warning:** CCR approaching work shortage
- **Rule Violations:** When planning rules are consistently overridden
- **Dependency Conflicts:** When dependencies affect planning decisions

### Multi-Schedule Work Item Management

#### Work Item Splitting Across Schedules
- **Partial Allocation:** Ability to schedule portion of work item to specific schedule
- **Remaining Effort Tracking:** System tracks unscheduled effort for work items
- **Cross-Schedule Visibility:** Show all schedule allocations for a work item
- **Total Effort Validation:** Ensure all effort is eventually scheduled

#### Work Item Schedule Allocation Interface
- **Split Work Item Function:** Interface to divide work item across multiple schedules
- **Effort Distribution:** Specify CCR hours allocated to each schedule
- **Schedule Sequence:** Track which schedules contain which portions of work item
- **Completion Dependencies:** Handle completion logic across multiple schedules

#### Work Item Display Enhancements
- **Schedule Allocation View:** List all schedules containing portions of work item
- **Effort Breakdown:** Show CCR hours allocated to each schedule
- **Completion Progress:** Track progress across multiple schedule instances
- **Remaining Effort:** Display unscheduled effort requiring future planning

### Planning Rules and Capacity Management

#### Rule Display and Reference
- **Rules Panel:** Display current Planning Rules for selected CCR
- **Rule Documentation:** Full rule descriptions and examples
- **Rule History:** Track changes to rules over time
- **Rule Compliance Indicators:** Visual feedback on rule adherence

#### Capacity Override Philosophy
- **Guidelines, Not Hard Limits:** Rules serve as guidance for planners
- **Visual Warnings:** Show capacity overruns but don't prevent planning
- **Planner Discretion:** Trust planners to make appropriate decisions
- **Capacity Visualization:** Clear display of planned vs. available capacity

#### Capacity Management Features
- **Real-time Capacity Tracking:** Running total of CCR hours scheduled
- **Over/Under Scheduling Visibility:** Clear indicators when capacity exceeded
- **Capacity Buffer Indicators:** Show planned capacity vs. actual CCR availability
- **Historical Capacity Analysis:** Track planning accuracy over time

### Planning Session Management

#### Multi-Draft Support
- **Multiple Draft Schedules:** Planners can work on several draft schedules simultaneously
- **Draft Management:** Save, load, and manage multiple draft schedules
- **Cross-Schedule Optimization:** Move work items between draft schedules
- **Resource Negotiation:** Support for iterative planning and re-planning

#### Draft Schedule Operations
- **Create Draft:** Start new draft schedule for specific time unit
- **Save Draft:** Preserve work-in-progress schedules
- **Load Draft:** Resume work on previously saved drafts
- **Compare Drafts:** Side-by-side comparison of different planning options
- **Merge Drafts:** Combine elements from multiple draft schedules

#### Schedule Finalization Process
- **Draft to Buffer:** Move completed schedule from draft to pre-constraint buffer
- **Schedule Locking:** Once in buffer, schedule sequence becomes immutable
- **Final Validation:** Last chance to review before committing to buffer
- **Release Confirmation:** Explicit confirmation required for schedule release

### Planning Interface Components

#### Available Work Items Panel
**Features Required:**
- **Work Item Filtering:** By project, priority, CCR resource, estimated hours, dependencies
- **Partial Scheduling Status:** Show which work items are partially scheduled
- **Remaining Effort Display:** Show unscheduled effort for each work item
- **Dependency Information:** Visual indicators for prerequisite work items

#### Schedule Builder Panel
**Features Required:**
- **Multi-Schedule View:** Display multiple draft schedules simultaneously
- **Partial Work Item Allocation:** Interface for splitting work items across schedules
- **Capacity Tracking per Schedule:** Individual capacity meters for each draft schedule
- **Cross-Schedule Movement:** Move work item allocations between schedules

#### CCR Resource Configuration Panel
**Features Required:**
- **Resource Assignment:** Select which resources comprise the CCR
- **Capacity Configuration:** Set CCR capacity based on resource availability
- **Resource Substitution Rules:** Define backup resources and equivalencies
- **Team Schedule Coordination:** Handle scheduling across team members

### Resource Substitution and Variation Management

#### Buffer-Based Variation Handling
- **Buffer Purpose:** Buffers naturally handle variation including resource unavailability
- **Non-CCR Unavailability:** When team members unavailable, buffer absorbs the variation over time
- **CCR Unavailability:** If CCR team member unavailable, more serious issue requiring team action
- **System Response:** No automatic substitution - team manages through existing buffer capacity
- **Visual Indicators:** Buffer penetration will show impact of resource constraints

#### Resource Availability Philosophy
- **Variation Expectation:** System designed expecting resource variation
- **Buffer Absorption:** Short-term unavailability handled by buffer zones
- **Team Responsibility:** Teams manage resource allocation within their CCR capacity
- **Escalation Only When Critical:** System alerts only when buffers indicate real problems

### Cross-CCR Dependency Management

#### Dependency Resolution Through Readiness
- **Ready State Validation:** Work items cannot be Ready if dependencies unresolved
- **Cross-CCR Dependency Tracking:** System tracks dependencies across different CCRs
- **Readiness Blocking:** Dependencies on other CCRs prevent work item readiness
- **Dependency Timeline:** Dependencies must be resolved before work item planning

#### Short Planning Horizon Benefits
- **Responsive Planning:** Small buffer sizes enable quick response to dependency changes
- **Late Dependency Resolution:** Dependencies can be resolved just before planning
- **Minimal Lead Time:** Days/hours from planning to CCR work pickup
- **Flexible Sequencing:** Can adjust plans based on dependency status changes

#### Dependency Management Process
- **Dependency Monitoring:** Track status of prerequisite work items across CCRs
- **Readiness Validation:** Automatic checking prevents scheduling dependent items
- **Cross-CCR Coordination:** Communication when dependencies affect multiple CCRs
- **Just-in-Time Resolution:** Dependencies resolved close to actual work timing

### Planning Horizon Management

#### Buffer-Defined Horizon
- **Planning Scope:** Length of pre-constraint buffer plus/minus few days/hours
- **Short-Term Focus:** Deliberately limited planning horizon for flexibility
- **Buffer Size Impact:** Larger buffers = longer planning horizon
- **Responsive Adjustment:** Can modify horizon based on buffer performance

#### Hierarchical Planning Integration
- **DBR Level:** Short-term tactical planning (days/weeks)
- **Portfolio Level:** Longer-term strategic planning (months/quarters)
- **Integration Points:** Roadmaps, CCPM plans, Story maps sequence MOVEs
- **Planning Handoff:** Strategic plans feed work items to DBR tactical planning

#### Planning Horizon Benefits
- **Reduced Waste:** Don't plan too far in advance
- **Increased Responsiveness:** Can adapt quickly to changes
- **Better Information:** Plan when you have better information
- **Flexible Sequencing:** Adjust priorities based on current conditions

### Notification Escalation and Visual Management

#### Self-Correcting System Design
- **Visual Escalation:** Empty pre-constraint buffer visible to entire team
- **Standup Visibility:** Daily standup meetings make buffer problems obvious
- **Team Accountability:** Everyone sees planning problems during reviews
- **Natural Pressure:** Empty buffers create immediate team pressure for action

#### Escalation Through Visibility
- **No Hidden Problems:** Buffer state visible to all team members
- **Peer Accountability:** Team members see when planners need to act
- **Immediate Consequences:** CCR starvation immediately visible
- **Team Response:** Natural team escalation when problems arise

#### Notification as Early Warning
- **Proactive Alerts:** Notifications provide early warning before crisis
- **Planning Support:** Help planners stay ahead of buffer depletion
- **Backup System:** Visual management is primary escalation mechanism
- **Redundant Safety:** Multiple ways to identify planning needs

#### Work Item Management Integration
- **Real-time Work Item Status:** Updates when work items change readiness status
- **Cross-Schedule Allocation Tracking:** Central tracking of work item schedule assignments
- **Completion Status Coordination:** Handle completion across multiple schedule instances

#### Buffer Board Integration
- **Schedule Release Handoff:** Seamless transfer of schedules to buffer zones
- **Capacity Coordination:** Ensure planning capacity matches buffer system capacity
- **Time Unit Synchronization:** Align planning time units with buffer time units

#### Notification System Integration
- **Alert Configuration:** Set up notification rules per CCR
- **Escalation Management:** Progressive notification as buffer zones penetrate
- **Integration APIs:** Connect with external messaging and notification systems

#### User Activity Tracking
- **Per-User Tracking:** Last viewed and last edited dates for each user-work item combination
- **Storage Model:** Efficient join table or relationship object
- **Performance Optimization:** Indexed for fast recent item queries
- **Data Retention:** Configurable retention period for activity metadata

#### Audit and Analytics
- **Change Tracking:** Complete audit trail of all modifications
- **User Analytics:** Usage patterns and productivity insights
- **System Monitoring:** Performance metrics and user behavior analysis
- **Compliance:** Support for regulatory audit requirements

### User Experience Principles

#### Ease of Use
- **Intuitive Navigation:** Clear information architecture
- **Minimal Clicks:** Common operations accessible within 2-3 clicks
- **Consistent Interface:** Uniform design patterns throughout application
- **Progressive Disclosure:** Show overview first, details on demand

#### Performance
- **Fast Loading:** Sub-2 second load times for all views
- **Responsive Design:** Smooth interaction across all device types
- **Offline Resilience:** Graceful handling of connectivity issues
- **Real-time Updates:** Live updates when other users make changes

#### Accessibility
- **WCAG Compliance:** Meet accessibility standards
- **Screen Reader Support:** Full keyboard and screen reader compatibility
- **Color Contrast:** Sufficient contrast for visual accessibility
- **Font Scaling:** Support for browser font size adjustments

### Core Time Management Assumptions

#### Time Progression
- **Time Never Stops:** The system mirrors reality where time progresses continuously
- **Automated Movement:** All schedules automatically move left at defined intervals
- **No Manual Repositioning:** Once schedules enter buffer zones, they cannot be manually moved
- **Standup Triggers:** Time progression can be triggered manually during standup meetings
- **Pause Capability:** System can be paused for planning/analysis but resumes normal progression

#### Schedule Lifecycle
- **Locked Sequence:** Once schedules move from Planning to buffer zones, their sequence is immutable
- **Only Forward Movement:** Schedules can only move left (forward in time), never backward
- **Completion Removal:** Schedules exit the system only when marked complete
- **No Zone Skipping:** Schedules must pass through each time slot sequentially

### Work Item Management Assumptions

#### Planning Stage Flexibility
- **Full Reordering:** Work items can be freely reordered within Planning stage
- **Capacity Constraints:** Cannot exceed time unit capacity when creating schedules
- **Ready Requirement:** Only Ready work items can be planned
- **Rules-Based Selection:** Planning follows agreed rules for work item selection

#### Buffer Zone Restrictions
- **No Modifications:** Work items in buffer zones cannot be reordered or modified
- **Progress Updates Only:** Can update task completion but not sequence or content
- **Status Changes:** Can update status indicators but not positioning

### User Interaction Assumptions

#### Primary Operations
- **Button-Based Control:** Core operations triggered by buttons, not drag-and-drop
- **Bulk Operations:** Multiple schedules can be processed simultaneously
- **Search/Filter First:** Users find items through search rather than visual scanning
- **View Switching:** Multiple view modes for different user roles and contexts

#### Access Control
- **Role-Based Permissions:** Different user types have different capabilities
- **Planning Authority:** Only designated planners can create schedules
- **Update Authority:** Workers can update progress, not sequence
- **Administrative Control:** System configuration requires elevated permissions

### Technical Architecture Assumptions

#### Real-Time Updates
- **Live Progress:** Task completion updates appear immediately
- **Concurrent Users:** Multiple users can interact simultaneously
- **Conflict Resolution:** System handles concurrent updates gracefully
- **Audit Trail:** All changes tracked with timestamps and user identification

#### Data Persistence
- **Immutable History:** Once time progresses, historical positions are preserved
- **Buffer Log:** All buffer states captured at each time unit
- **Recovery Capability:** System can restore previous states if needed
- **Backup Operations:** Regular data backups maintain system integrity

### Display and Visualization Assumptions

#### Screen Real Estate
- **Multi-Monitor Support:** Designed for large displays in team areas
- **Mobile Responsive:** Secondary interface for mobile/tablet access
- **Always Visible:** Primary board displayed continuously in team workspace
- **Quick Reference:** Key information visible at a glance

#### Information Density
- **Hierarchical Detail:** Multiple levels of information detail available
- **Progressive Disclosure:** Show overview first, details on demand
- **Context Switching:** Easy movement between different view modes
- **Status Clarity:** Current state immediately obvious

### Business Logic Assumptions

#### Constraint Management
- **Single CCR per Row:** Each buffer row focuses on one constraint
- **Skill-Based Constraints:** CCRs typically represent key skills or roles
- **Resource Flexibility:** Non-CCR resources can move between rows as needed
- **Priority Hierarchies:** Clear rules for resource allocation across rows

#### Planning Rules
- **Consistent Application:** Rules applied uniformly across all planning sessions
- **Configurable Logic:** Rules can be modified through system configuration
- **Violation Prevention:** System prevents rule violations during planning
- **Exception Handling:** Process for handling rule conflicts or exceptions

### Performance Assumptions

#### Response Time
- **Interactive Performance:** UI responds within 200ms for common operations
- **Bulk Operations:** Large operations (standup progression) complete within 5 seconds
- **Search Performance:** Search results appear within 1 second
- **Real-Time Updates:** Progress updates propagate within 30 seconds

#### Scalability
- **Team Size:** Supports 5-50 people per CCR row
- **Work Volume:** Handles 100-1000 active work items simultaneously
- **Time Horizon:** Manages 2-12 weeks of buffer depth
- **Concurrent Users:** Supports 10-100 simultaneous users

## Backlog Management Requirements

### System Architecture Assumptions
- **Web-based application** - Multi-user concurrent access
- **Real-time collaboration** - Multiple users can work simultaneously
- **Browser-based interface** - No client installation required
- **Responsive design** - Works on desktop, tablet, and mobile devices

### User Roles and Access (Future Consideration)
- **Current assumption:** All users can see all work items
- **Future requirement:** Role-based access control system
- **Anticipated roles:**
  - Planners (can create/modify schedules)
  - Workers (can update progress)
  - Managers (can view all, configure system)
  - Viewers (read-only access)

### Project/MOVE Management Requirements

**Note:** Projects and MOVEs are treated as the same entity type with unified management.

#### Project/MOVE Data Management
- **Search Projects/MOVEs:** Text search across names and descriptions
- **Filter Projects/MOVEs:** By status, owner, date ranges, value ranges
- **List Projects/MOVEs:** Tabular and card views with sorting options
- **Add Projects/MOVEs:** Create new projects/MOVEs with required attributes
- **Edit Projects/MOVEs:** Modify existing project/MOVE details
- **Delete Projects/MOVEs:** Remove projects/MOVEs (with dependency checking)

#### Project/MOVE Attributes Required
- Unique Project/MOVE ID (auto-generated)
- Project/MOVE Name
- Project/MOVE Description
- Type (Project or MOVE - for display/organizational purposes)
- Status (planning, active, on-hold, completed)
- Owner/Lead
- Created Date
- Estimated Total Value
- Target Completion Date
- Associated Work Items Count

#### Project/MOVE Operations
- **Bulk Operations:** Select multiple projects/MOVEs for status updates
- **Project/MOVE Hierarchy:** Support for parent/child relationships
- **Project/MOVE Templates:** Reusable project/MOVE structures
- **Project/MOVE Archiving:** Soft delete for completed projects/MOVEs

### Work Item Management Requirements

#### Work Item Data Management
- **Search Work Items:** Text search across titles, descriptions, tags
- **Filter Work Items:** By project, status, priority, assignee, due date
- **List Work Items:** Multiple view formats (table, cards, timeline)
- **Add Work Items:** Create new work items with full attribute set
- **Edit Work Items:** Modify existing work item details
- **Delete Work Items:** Remove work items (with dependency checking)

#### Work Item Attributes Required
- Unique Work Item ID (auto-generated)
- Work Item Title
- Work Item Description
- Project/MOVE Association
- Status (backlog, ready, in-progress, done)
- Priority Level (low, medium, high, critical)
- Estimated Total Hours
- CCR Hours Required
- Sales Price
- Variable Costs
- Throughput Calculation (auto-calculated)
- Due Date
- Created Date
- Assigned To (person/team)
- Task/Todo List
- Comments/Notes History
- **Dependencies:** List of work items this item depends on (prerequisites)
- **Dependents:** List of work items that depend on this item (automatically calculated)

#### Work Item Operations
- **Bulk Operations:** Select multiple work items for updates
- **Dependency Management:** Add/remove dependencies between work items
- **Dependency Visualization:** Show dependency chains and impact analysis
- **Dependency Validation:** Prevent circular dependencies
- **Work Item Templates:** Reusable work item structures
- **Work Item Cloning:** Duplicate similar work items
- **Status Transitions:** Workflow rules for status changes

### Work Item Dependency Management

#### Dependency Types
- **Finish-to-Start:** Prerequisite work item must be completed before this item can start
- **Start-to-Start:** Prerequisite work item must start before this item can start
- **Finish-to-Finish:** Prerequisite work item must finish before this item can finish
- **Start-to-Finish:** Prerequisite work item must start before this item can finish

#### Dependency Operations
- **Add Dependency:** Link one work item as prerequisite to another
- **Remove Dependency:** Break dependency link between work items
- **View Dependencies:** Show all dependencies for a work item
- **Impact Analysis:** Show which work items will be affected by changes
- **Critical Path:** Identify work items on the critical path
- **Dependency Conflicts:** Alert when dependencies conflict with scheduling

#### Dependency Validation Rules
- **No Circular Dependencies:** System prevents A depends on B, B depends on A
- **Cross-Project Dependencies:** Allow dependencies between work items in different projects
- **Status Consistency:** Dependent work items cannot be Ready if prerequisites aren't Done
- **Scheduling Impact:** Dependencies affect when work items can be planned

### Relationship Management
- **Work Items belong to Projects/MOVEs:** One-to-many relationship
- **Project/MOVE can have multiple Work Items:** Parent-child hierarchy
- **Cross-project dependencies:** Work items can depend on items from other projects
- **Resource assignments:** People can work on multiple projects

### Search and Filter Requirements

#### Search Capabilities
- **Global Search:** Search across all projects and work items
- **Scoped Search:** Search within specific projects
- **Advanced Search:** Multiple criteria (AND/OR logic)
- **Search History:** Recent searches saved
- **Search Suggestions:** Auto-complete and suggestions

#### Filter Options
- **Project Filters:** Status, owner, date ranges, value
- **Work Item Filters:** Project, status, priority, assignee, due date, tags
- **Saved Filters:** Users can save frequently used filter combinations
- **Quick Filters:** One-click common filter options
- **Dynamic Filters:** Filter options update based on current data

### User Interface Requirements

#### Navigation Structure
- **Primary Tabs:** Projects, Work Items, (future: Reports, Configuration)
- **Secondary Navigation:** Within each tab, sub-views available
- **Breadcrumbs:** Show current location in hierarchy
- **Quick Actions:** Common operations easily accessible

#### List/Grid Views
- **Table View:** Detailed information in columns
- **Card View:** Visual cards with key information
- **Timeline View:** Work items arranged by due dates
- **Kanban View:** Work items by status columns

#### Interaction Patterns
- **Single-click:** Select items
- **Double-click:** Open item details
- **Right-click:** Context menu with relevant actions
- **Keyboard shortcuts:** Power user efficiency
- **Bulk selection:** Checkbox selection for multiple items

### Data Validation Requirements

#### Project Validation
- **Required Fields:** Name, description, owner, status
- **Unique Constraints:** Project ID, project name within organization
- **Business Rules:** Cannot delete projects with active work items
- **Date Validation:** Target dates must be future dates

#### Work Item Validation
- **Required Fields:** Title, description, project association, estimated hours
- **Business Rules:** CCR hours cannot exceed total hours
- **Financial Validation:** Sales price must be greater than variable costs
- **Dependency Validation:** Cannot create circular dependencies

### Performance Requirements

#### Response Time Targets
- **Search Results:** < 2 seconds for any search query
- **List Loading:** < 3 seconds for up to 1000 items
- **Item Creation:** < 1 second for new items
- **Bulk Operations:** < 10 seconds for up to 100 items

#### Scalability Targets
- **Projects:** Support up to 500 active projects
- **Work Items:** Support up to 10,000 active work items
- **Concurrent Users:** Support 50+ simultaneous users
- **Search Performance:** Maintain speed with full data load

#### External Systems
- **Time Tracking:** Integrates with existing time tracking tools
- **Project Management:** Imports/exports data from PM systems
- **Identity Management:** Uses organization's authentication system
- **Notification Systems:** Leverages existing communication channels

#### Data Exchange
- **API-First Design:** All functionality available through APIs
- **Import/Export:** Standard formats for data exchange
- **Reporting Integration:** Data available for external reporting tools
- **Backup Integration:** Works with organizational backup systems

To support these features, our data structure needs:

#### Work Item Enhancements
- **Project association** - Link work items to parent projects
- **Detailed descriptions** - Full text storage for task details
- **Visual markers** - Color coding, symbols, status indicators
- **Time tracking** - Creation time, age calculation, duration tracking

#### Resource/Person Management
- **Skill capabilities** - Multiple capability channels per person
- **Capacity tracking** - Available time, utilization percentages
- **Assignment history** - Track who worked on what when

#### Buffer Analytics
- **Age calculations** - Time since work item creation/entry
- **Penetration metrics** - Percentage calculations for buffer zones
- **Utilization tracking** - Capacity usage across resources

#### Project Organization
- **Project hierarchies** - Parent-child relationships
- **Project metadata** - Colors, priorities, descriptions
- **Cross-project dependencies** - Linking related work across projects

### Usability First
- **Rough and Ready > Pretty:** Functionality trumps aesthetics
- **Zero Friction:** Any barrier to updating kills adoption
- **Physical Success Factors:** Visible location, simple materials (paper, pens, clips)
- **Digital Challenge:** Must be exceptionally slick to compete with physical simplicity

### Core Requirements
- **Speed over Beauty:** Fast interaction over visual polish
- **Touch-Friendly:** Drag-and-drop as natural as physical manipulation
- **Always Visible:** Dashboard always accessible
- **Minimal Clicks:** Single-action updates
- **Self-Organization:** Answers "What should I do next?" without asking

## Technical Considerations

### Movement Rules Implementation
- **Free Reordering:** Easy drag-and-drop in Backlog and Ready stages
- **Locked Zones:** No reordering in buffer zones
- **Planning Gate:** Clear transition from flexible to committed
- **Ready Validation:** System enforces only Ready items can be planned

### Time Management
- **Scheduled Updates:** Automatic time unit progression
- **Standup Interface:** Easy review and completion marking
- **Time Visualization:** Clear representation of time passage
- **Cannot Stop Time:** System enforces forward movement

### Data Architecture
- **Buffer Log:** Automatic capture at each time unit
- **Historical Dashboard:** Charts and trends over time
- **Export Capability:** Data available for external analysis
- **Alert Patterns:** Identify recurring problems

## Success Metrics

### System Health Indicators
- **Buffer penetration:** How often work enters yellow/red zones
- **Schedule variance:** Consistency of on-time completion
- **CCR utilization:** Maximizing constraint productivity
- **Flow predictability:** Reduced variation in work completion

### Behavioral Outcomes
- **Self-direction:** Reduced need for management intervention
- **Priority clarity:** Team knows what to work on next
- **Proactive responses:** Team acts on buffer signals before crises
- **Continuous improvement:** Data-driven system optimization
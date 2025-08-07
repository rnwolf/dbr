# DBR Database Seed Data Expansion Plan

## Current Seed Data (Already Implemented)

### 🏢 Organizations
- **Default Organization**
  - Name: "Default Organization"
  - Description: "Default organization for MVP testing and development"
  - Status: ACTIVE
  - Contact Email: admin@default.org
  - Country: US
  - Subscription Level: basic

### 👥 Users (5 test users)
| Username | Email | Password | Role | System Role ID |
|----------|-------|----------|------|----------------|
| `admin` | admin@test.com | `admin123` | Super Admin | (role_id) |
| `orgadmin` | orgadmin@test.com | `orgadmin123` | Organization Admin | (role_id) |
| `planner` | planner@test.com | `planner123` | Planner | (role_id) |
| `worker` | worker@test.com | `worker123` | Worker | (role_id) |
| `viewer` | viewer@test.com | `viewer123` | Viewer | (role_id) |

### 🎭 Roles (5 system roles)
| Role Name | Description |
|-----------|-------------|
| Super Admin | System administrator with full access to all features and organizations |
| Organization Admin | Organization administrator who can manage users and settings within their organization |
| Planner | Can create and manage work items, schedules, and advance time |
| Worker | Can update work items and view reports |
| Viewer | Read-only access to view reports and dashboards |

### 🔗 Organization Memberships
- All 5 users are members of "Default Organization"
- Each user's organization role matches their system role
- All memberships are ACCEPTED status
- All invited by admin user
- Join dates set to current timestamp

## Proposed Additional Seed Data

### 🏢 Additional Organizations
```python
additional_organization_definitions = [
    {
        "name": "TechCorp Solutions",
        "description": "Technology consulting and software development company",
        "status": OrganizationStatus.ACTIVE,
        "contact_email": "admin@techcorp.com",
        "country": "US",
        "subscription_level": "premium"
    },
    {
        "name": "StartupVenture Inc",
        "description": "Early-stage startup focused on innovative solutions",
        "status": OrganizationStatus.ACTIVE,
        "contact_email": "founder@startupventure.com", 
        "country": "CA",
        "subscription_level": "basic"
    }
]
```

### 👥 Additional Users (Multi-Organization Testing)
```python
additional_user_definitions = [
    # TechCorp Solutions Users
    ("techcorp_admin", "admin@techcorp.com", "techcorp123", "TechCorp Admin", RoleName.ORGANIZATION_ADMIN),
    ("techcorp_planner", "planner@techcorp.com", "techcorp123", "TechCorp Planner", RoleName.PLANNER),
    ("techcorp_worker1", "worker1@techcorp.com", "techcorp123", "TechCorp Senior Developer", RoleName.WORKER),
    ("techcorp_worker2", "worker2@techcorp.com", "techcorp123", "TechCorp Frontend Developer", RoleName.WORKER),
    ("techcorp_worker3", "worker3@techcorp.com", "techcorp123", "TechCorp Backend Developer", RoleName.WORKER),
    ("techcorp_worker4", "worker4@techcorp.com", "techcorp123", "TechCorp QA Engineer", RoleName.WORKER),
    
    # StartupVenture Inc Users  
    ("startup_founder", "founder@startupventure.com", "startup123", "Startup Founder", RoleName.ORGANIZATION_ADMIN),
    ("startup_dev", "dev@startupventure.com", "startup123", "Startup Lead Developer", RoleName.PLANNER),
    ("startup_worker1", "worker1@startupventure.com", "startup123", "Startup Full-Stack Dev", RoleName.WORKER),
    ("startup_worker2", "worker2@startupventure.com", "startup123", "Startup UI/UX Designer", RoleName.WORKER),
    
    # Default Organization Additional Workers (to supplement existing worker@test.com)
    ("default_worker2", "worker2@test.com", "default123", "Default Frontend Developer", RoleName.WORKER),
    ("default_worker3", "worker3@test.com", "default123", "Default Backend Developer", RoleName.WORKER),
    ("default_worker4", "worker4@test.com", "default123", "Default QA Tester", RoleName.WORKER),
    ("default_worker5", "worker5@test.com", "default123", "Default DevOps Engineer", RoleName.WORKER),
    
    # Cross-Organization Users (for testing multi-org membership)
    ("consultant", "consultant@freelance.com", "consultant123", "External Consultant", RoleName.WORKER),
    ("contractor", "contractor@external.com", "contractor123", "External Contractor", RoleName.WORKER),
    
    # Users with NO organization membership (for testing access denial)
    ("outsider", "outsider@external.com", "outsider123", "External User", RoleName.VIEWER),
    ("prospect", "prospect@potential.com", "prospect123", "Potential Client", RoleName.VIEWER),
]
```

### 🔗 Multi-Organization Membership Matrix
```python
# Organization membership definitions
membership_definitions = [
    # Default Organization (PRESERVE EXISTING - DO NOT CHANGE)
    # admin, orgadmin, planner, worker, viewer (already exists)
    
    # TechCorp Solutions memberships
    ("TechCorp Solutions", "admin@test.com", RoleName.SUPER_ADMIN),  # Super admin has access
    ("TechCorp Solutions", "admin@techcorp.com", RoleName.ORGANIZATION_ADMIN),
    ("TechCorp Solutions", "planner@techcorp.com", RoleName.PLANNER), 
    ("TechCorp Solutions", "worker1@techcorp.com", RoleName.WORKER),
    ("TechCorp Solutions", "worker2@techcorp.com", RoleName.WORKER),
    ("TechCorp Solutions", "worker3@techcorp.com", RoleName.WORKER),
    ("TechCorp Solutions", "worker4@techcorp.com", RoleName.WORKER),
    ("TechCorp Solutions", "consultant@freelance.com", RoleName.WORKER),  # Cross-org user
    
    # StartupVenture Inc memberships
    ("StartupVenture Inc", "admin@test.com", RoleName.SUPER_ADMIN),  # Super admin has access
    ("StartupVenture Inc", "founder@startupventure.com", RoleName.ORGANIZATION_ADMIN),
    ("StartupVenture Inc", "dev@startupventure.com", RoleName.PLANNER),
    ("StartupVenture Inc", "worker1@startupventure.com", RoleName.WORKER),
    ("StartupVenture Inc", "worker2@startupventure.com", RoleName.WORKER),
    ("StartupVenture Inc", "contractor@external.com", RoleName.WORKER),  # Cross-org user
    
    # Default Organization additional memberships
    ("Default Organization", "worker2@test.com", RoleName.WORKER),
    ("Default Organization", "worker3@test.com", RoleName.WORKER),
    ("Default Organization", "worker4@test.com", RoleName.WORKER),
    ("Default Organization", "worker5@test.com", RoleName.WORKER),
    ("Default Organization", "consultant@freelance.com", RoleName.WORKER),  # Cross-org user
    
    # NO MEMBERSHIPS for outsider@external.com and prospect@potential.com
    # These users should be denied access to any organization data
]
```

### 🏭 Organization-Scoped CCRs (Capacity Constrained Resources)
```python
ccr_definitions = [
    # Default Organization CCRs
    {
        "organization_id": "default_org_id",
        "name": "Development Team",
        "description": "Software development team with full-stack capabilities",
        "ccr_type": CCRType.TEAM_BASED,
        "capacity_per_time_unit": 40.0,  # 40 hours per week
        "time_unit": "week"
    },
    {
        "organization_id": "default_org_id",
        "name": "QA Testing",
        "description": "Quality assurance and testing team",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 20.0,  # 20 hours per week
        "time_unit": "week"
    },
    {
        "organization_id": "default_org_id",
        "name": "DevOps Pipeline",
        "description": "CI/CD pipeline and deployment infrastructure",
        "ccr_type": CCRType.EQUIPMENT_BASED,
        "capacity_per_time_unit": 10.0,  # 10 hours per week
        "time_unit": "week"
    },
    {
        "organization_id": "default_org_id",
        "name": "UI/UX Design",
        "description": "User interface and experience design team",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 15.0,  # 15 hours per week
        "time_unit": "week"
    },
    
    # TechCorp Solutions CCRs
    {
        "organization_id": "techcorp_org_id",
        "name": "Senior Developers",
        "description": "Senior development team for enterprise solutions",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 60.0,  # 60 hours per week (larger team)
        "time_unit": "week"
    },
    {
        "organization_id": "techcorp_org_id",
        "name": "Architecture Review",
        "description": "Technical architecture review and approval process",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 8.0,  # 8 hours per week (bottleneck)
        "time_unit": "week"
    },
    {
        "organization_id": "techcorp_org_id",
        "name": "Client Deployment",
        "description": "Client-specific deployment and configuration",
        "ccr_type": CCRType.EQUIPMENT_BASED,
        "capacity_per_time_unit": 12.0,  # 12 hours per week
        "time_unit": "week"
    },
    
    # StartupVenture Inc CCRs
    {
        "organization_id": "startup_org_id",
        "name": "Full-Stack Developer",
        "description": "Single full-stack developer (startup constraint)",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 35.0,  # 35 hours per week (one person)
        "time_unit": "week"
    },
    {
        "organization_id": "startup_org_id",
        "name": "Founder Review",
        "description": "Founder approval for major features",
        "ccr_type": CCRType.SKILL_BASED,
        "capacity_per_time_unit": 5.0,  # 5 hours per week (major bottleneck)
        "time_unit": "week"
    }
]
```

### 🎛️ Organization-Scoped Board Configurations
```python
board_config_definitions = [
    # Default Organization Boards
    {
        "organization_id": "default_org_id",
        "name": "Main Development Board",
        "description": "Primary DBR board for development workflow",
        "ccr_id": "development_team_ccr_id",  # References Development Team CCR
        "pre_constraint_buffer_size": 5,
        "post_constraint_buffer_size": 3,
        "time_unit": "week",
        "is_active": True
    },
    {
        "organization_id": "default_org_id",
        "name": "QA Testing Board", 
        "description": "DBR board focused on QA testing workflow",
        "ccr_id": "qa_testing_ccr_id",  # References QA Testing CCR
        "pre_constraint_buffer_size": 3,
        "post_constraint_buffer_size": 2,
        "time_unit": "week",
        "is_active": True
    },
    
    # TechCorp Solutions Boards
    {
        "organization_id": "techcorp_org_id",
        "name": "Enterprise Development Board",
        "description": "DBR board for enterprise client projects",
        "ccr_id": "senior_developers_ccr_id",  # References Senior Developers CCR
        "pre_constraint_buffer_size": 4,
        "post_constraint_buffer_size": 2,
        "time_unit": "week",
        "is_active": True
    },
    {
        "organization_id": "techcorp_org_id",
        "name": "Architecture Review Board",
        "description": "DBR board for architecture review process",
        "ccr_id": "architecture_review_ccr_id",  # References Architecture Review CCR
        "pre_constraint_buffer_size": 6,  # Longer buffer due to bottleneck
        "post_constraint_buffer_size": 1,
        "time_unit": "week",
        "is_active": True
    },
    
    # StartupVenture Inc Boards
    {
        "organization_id": "startup_org_id",
        "name": "MVP Development Board",
        "description": "DBR board for MVP feature development",
        "ccr_id": "full_stack_developer_ccr_id",  # References Full-Stack Developer CCR
        "pre_constraint_buffer_size": 3,
        "post_constraint_buffer_size": 2,
        "time_unit": "week",
        "is_active": True
    }
]
```

### 📁 Organization-Scoped Collections (Projects/MOVEs)
```python
collection_definitions = [
    # Default Organization Collections
    {
        "organization_id": "default_org_id",
        "name": "Customer Portal Enhancement",
        "description": "Enhance customer portal with new features and improved UX",
        "status": CollectionStatus.ACTIVE,
        "owner_user_id": "planner@test.com",  # planner user from Default Org
        "estimated_sales_price": 50000.0,
        "estimated_variable_cost": 15000.0,
        "url": "https://github.com/defaultorg/customer-portal"
    },
    {
        "organization_id": "default_org_id",
        "name": "Mobile App Development",
        "description": "Develop native mobile application for iOS and Android",
        "status": CollectionStatus.PLANNING,
        "owner_user_id": "planner@test.com",  # planner user from Default Org
        "estimated_sales_price": 75000.0,
        "estimated_variable_cost": 25000.0,
        "url": "https://github.com/defaultorg/mobile-app"
    },
    {
        "organization_id": "default_org_id",
        "name": "API Integration Project",
        "description": "Integrate with third-party APIs for enhanced functionality",
        "status": CollectionStatus.ACTIVE,
        "owner_user_id": "orgadmin@test.com",  # orgadmin user from Default Org
        "estimated_sales_price": 30000.0,
        "estimated_variable_cost": 10000.0,
        "url": "https://github.com/defaultorg/api-integration"
    },
    {
        "organization_id": "default_org_id",
        "name": "Security Audit Implementation",
        "description": "Implement security improvements based on audit findings",
        "status": CollectionStatus.ON_HOLD,
        "owner_user_id": "orgadmin@test.com",  # orgadmin user from Default Org
        "estimated_sales_price": 20000.0,
        "estimated_variable_cost": 8000.0,
        "url": "https://github.com/defaultorg/security-audit"
    },
    
    # TechCorp Solutions Collections
    {
        "organization_id": "techcorp_org_id",
        "name": "Enterprise CRM System",
        "description": "Custom CRM solution for large enterprise client",
        "status": CollectionStatus.ACTIVE,
        "owner_user_id": "planner@techcorp.com",  # TechCorp planner
        "estimated_sales_price": 250000.0,
        "estimated_variable_cost": 80000.0,
        "url": "https://github.com/techcorp/enterprise-crm"
    },
    {
        "organization_id": "techcorp_org_id",
        "name": "Cloud Migration Project",
        "description": "Migrate legacy systems to cloud infrastructure",
        "status": CollectionStatus.ACTIVE,
        "owner_user_id": "admin@techcorp.com",  # TechCorp admin
        "estimated_sales_price": 180000.0,
        "estimated_variable_cost": 60000.0,
        "url": "https://github.com/techcorp/cloud-migration"
    },
    {
        "organization_id": "techcorp_org_id",
        "name": "Microservices Architecture",
        "description": "Refactor monolith to microservices architecture",
        "status": CollectionStatus.PLANNING,
        "owner_user_id": "planner@techcorp.com",  # TechCorp planner
        "estimated_sales_price": 320000.0,
        "estimated_variable_cost": 120000.0,
        "url": "https://github.com/techcorp/microservices"
    },
    
    # StartupVenture Inc Collections
    {
        "organization_id": "startup_org_id",
        "name": "MVP Core Features",
        "description": "Essential features for minimum viable product launch",
        "status": CollectionStatus.ACTIVE,
        "owner_user_id": "founder@startupventure.com",  # Startup founder
        "estimated_sales_price": 15000.0,
        "estimated_variable_cost": 5000.0,
        "url": "https://github.com/startupventure/mvp-core"
    },
    {
        "organization_id": "startup_org_id",
        "name": "User Onboarding Flow",
        "description": "Streamlined user registration and onboarding process",
        "status": CollectionStatus.PLANNING,
        "owner_user_id": "dev@startupventure.com",  # Startup developer
        "estimated_sales_price": 8000.0,
        "estimated_variable_cost": 3000.0,
        "url": "https://github.com/startupventure/onboarding"
    },
    {
        "organization_id": "startup_org_id",
        "name": "Analytics Dashboard",
        "description": "Basic analytics and reporting for early users",
        "status": CollectionStatus.COMPLETED,
        "owner_user_id": "dev@startupventure.com",  # Startup developer
        "estimated_sales_price": 5000.0,
        "estimated_variable_cost": 2000.0,
        "url": "https://github.com/startupventure/analytics"
    }
]
```

### 📋 Organization-Scoped Work Items with User Assignments
```python
work_item_definitions = [
    # Default Organization Work Items
    # Customer Portal Enhancement Collection
    {
        "organization_id": "default_org_id",
        "collection_id": "customer_portal_collection_id",
        "title": "Redesign User Dashboard",
        "description": "Create modern, responsive dashboard with improved navigation",
        "status": WorkItemStatus.IN_PROGRESS,
        "priority": WorkItemPriority.HIGH,
        "estimated_total_hours": 16.0,
        "estimated_sales_price": 8000.0,
        "estimated_variable_cost": 2400.0,
        "assigned_user_id": "worker2@test.com",  # Assigned to Default Frontend Developer
        "ccr_hours_required": {
            "development_team": 12.0,
            "ui_ux_design": 4.0
        },
        "tasks": [
            {"id": 1, "title": "Create wireframes", "completed": True, "assigned_user_id": "worker2@test.com"},
            {"id": 2, "title": "Design mockups", "completed": True, "assigned_user_id": "worker2@test.com"},
            {"id": 3, "title": "Implement frontend", "completed": False, "assigned_user_id": "worker2@test.com"},
            {"id": 4, "title": "Add responsive features", "completed": False, "assigned_user_id": "worker2@test.com"}
        ]
    },
    {
        "organization_id": "default_org_id",
        "collection_id": "customer_portal_collection_id",
        "title": "Implement Advanced Search",
        "description": "Add advanced search functionality with filters and sorting",
        "status": WorkItemStatus.IN_PROGRESS,
        "priority": WorkItemPriority.MEDIUM,
        "estimated_total_hours": 12.0,
        "estimated_sales_price": 6000.0,
        "estimated_variable_cost": 1800.0,
        "assigned_user_id": "worker3@test.com",  # Assigned to Default Backend Developer
        "ccr_hours_required": {
            "development_team": 10.0,
            "qa_testing": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Design search API", "completed": True, "assigned_user_id": "worker3@test.com"},
            {"id": 2, "title": "Implement backend search", "completed": True, "assigned_user_id": "worker3@test.com"},
            {"id": 3, "title": "Create search UI", "completed": False, "assigned_user_id": "worker2@test.com"},
            {"id": 4, "title": "Add filter options", "completed": False, "assigned_user_id": "worker2@test.com"},
            {"id": 5, "title": "Test search functionality", "completed": False, "assigned_user_id": "worker4@test.com"}
        ]
    },
    {
        "organization_id": "default_org_id",
        "collection_id": "customer_portal_collection_id",
        "title": "User Profile Management",
        "description": "Allow users to manage their profiles and preferences",
        "status": WorkItemStatus.READY,
        "priority": WorkItemPriority.MEDIUM,
        "estimated_total_hours": 8.0,
        "estimated_sales_price": 4000.0,
        "estimated_variable_cost": 1200.0,
        "assigned_user_id": "worker@test.com",  # Assigned to original Default Worker
        "ccr_hours_required": {
            "development_team": 6.0,
            "ui_ux_design": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Design profile page", "completed": False, "assigned_user_id": "worker@test.com"},
            {"id": 2, "title": "Implement profile editing", "completed": False, "assigned_user_id": "worker@test.com"},
            {"id": 3, "title": "Add preference settings", "completed": False, "assigned_user_id": "worker@test.com"}
        ]
    },
    {
        "organization_id": "default_org_id",
        "collection_id": "api_integration_collection_id",
        "title": "Payment Gateway Integration",
        "description": "Integrate Stripe payment gateway for processing payments",
        "status": WorkItemStatus.DONE,
        "priority": WorkItemPriority.CRITICAL,
        "estimated_total_hours": 14.0,
        "estimated_sales_price": 10000.0,
        "estimated_variable_cost": 3000.0,
        "assigned_user_id": "worker5@test.com",  # Assigned to Default DevOps Engineer
        "ccr_hours_required": {
            "development_team": 12.0,
            "qa_testing": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Set up Stripe account", "completed": True, "assigned_user_id": "worker5@test.com"},
            {"id": 2, "title": "Implement payment API", "completed": True, "assigned_user_id": "worker3@test.com"},
            {"id": 3, "title": "Add payment UI", "completed": True, "assigned_user_id": "worker2@test.com"},
            {"id": 4, "title": "Test payment flow", "completed": True, "assigned_user_id": "worker4@test.com"},
            {"id": 5, "title": "Handle error cases", "completed": True, "assigned_user_id": "worker3@test.com"}
        ]
    },
    
    # TechCorp Solutions Work Items
    {
        "organization_id": "techcorp_org_id",
        "collection_id": "enterprise_crm_collection_id",
        "title": "Customer Data Migration",
        "description": "Migrate existing customer data to new CRM system",
        "status": WorkItemStatus.IN_PROGRESS,
        "priority": WorkItemPriority.CRITICAL,
        "estimated_total_hours": 40.0,
        "estimated_sales_price": 50000.0,
        "estimated_variable_cost": 15000.0,
        "assigned_user_id": "worker1@techcorp.com",  # TechCorp Senior Developer
        "ccr_hours_required": {
            "senior_developers": 35.0,
            "architecture_review": 5.0
        },
        "tasks": [
            {"id": 1, "title": "Analyze legacy data structure", "completed": True, "assigned_user_id": "worker1@techcorp.com"},
            {"id": 2, "title": "Design migration scripts", "completed": True, "assigned_user_id": "worker1@techcorp.com"},
            {"id": 3, "title": "Implement data transformation", "completed": False, "assigned_user_id": "worker3@techcorp.com"},
            {"id": 4, "title": "Test migration process", "completed": False, "assigned_user_id": "worker4@techcorp.com"},
            {"id": 5, "title": "Execute production migration", "completed": False, "assigned_user_id": "worker1@techcorp.com"}
        ]
    },
    {
        "organization_id": "techcorp_org_id",
        "collection_id": "enterprise_crm_collection_id",
        "title": "Advanced Reporting Module",
        "description": "Build comprehensive reporting and analytics dashboard",
        "status": WorkItemStatus.READY,
        "priority": WorkItemPriority.HIGH,
        "estimated_total_hours": 30.0,
        "estimated_sales_price": 40000.0,
        "estimated_variable_cost": 12000.0,
        "assigned_user_id": "worker2@techcorp.com",  # TechCorp Frontend Developer
        "ccr_hours_required": {
            "senior_developers": 25.0,
            "architecture_review": 5.0
        },
        "tasks": [
            {"id": 1, "title": "Design report templates", "completed": False, "assigned_user_id": "worker2@techcorp.com"},
            {"id": 2, "title": "Implement data aggregation", "completed": False, "assigned_user_id": "worker3@techcorp.com"},
            {"id": 3, "title": "Create visualization components", "completed": False, "assigned_user_id": "worker2@techcorp.com"},
            {"id": 4, "title": "Add export functionality", "completed": False, "assigned_user_id": "worker2@techcorp.com"}
        ]
    },
    {
        "organization_id": "techcorp_org_id",
        "collection_id": "cloud_migration_collection_id",
        "title": "Database Migration to AWS",
        "description": "Migrate on-premise databases to AWS RDS",
        "status": WorkItemStatus.STANDBY,
        "priority": WorkItemPriority.HIGH,
        "estimated_total_hours": 25.0,
        "estimated_sales_price": 35000.0,
        "estimated_variable_cost": 10000.0,
        "assigned_user_id": "consultant@freelance.com",  # Cross-org consultant
        "ccr_hours_required": {
            "senior_developers": 20.0,
            "client_deployment": 5.0
        },
        "tasks": [
            {"id": 1, "title": "Assess current database schema", "completed": False, "assigned_user_id": "consultant@freelance.com"},
            {"id": 2, "title": "Set up AWS RDS instances", "completed": False, "assigned_user_id": "consultant@freelance.com"},
            {"id": 3, "title": "Configure backup strategies", "completed": False, "assigned_user_id": "consultant@freelance.com"}
        ]
    },
    
    # StartupVenture Inc Work Items
    {
        "organization_id": "startup_org_id",
        "collection_id": "mvp_core_collection_id",
        "title": "User Authentication System",
        "description": "Implement secure user registration and login",
        "status": WorkItemStatus.DONE,
        "priority": WorkItemPriority.CRITICAL,
        "estimated_total_hours": 12.0,
        "estimated_sales_price": 5000.0,
        "estimated_variable_cost": 1500.0,
        "assigned_user_id": "worker1@startupventure.com",  # Startup Full-Stack Dev
        "ccr_hours_required": {
            "full_stack_developer": 10.0,
            "founder_review": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Design authentication flow", "completed": True, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 2, "title": "Implement user registration", "completed": True, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 3, "title": "Add password reset", "completed": True, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 4, "title": "Test security measures", "completed": True, "assigned_user_id": "worker1@startupventure.com"}
        ]
    },
    {
        "organization_id": "startup_org_id",
        "collection_id": "mvp_core_collection_id",
        "title": "Core Product Features",
        "description": "Essential features for MVP launch",
        "status": WorkItemStatus.IN_PROGRESS,
        "priority": WorkItemPriority.HIGH,
        "estimated_total_hours": 18.0,
        "estimated_sales_price": 8000.0,
        "estimated_variable_cost": 2500.0,
        "assigned_user_id": "worker1@startupventure.com",  # Startup Full-Stack Dev
        "ccr_hours_required": {
            "full_stack_developer": 15.0,
            "founder_review": 3.0
        },
        "tasks": [
            {"id": 1, "title": "Build main dashboard", "completed": True, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 2, "title": "Implement core workflow", "completed": False, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 3, "title": "Add data persistence", "completed": False, "assigned_user_id": "worker1@startupventure.com"},
            {"id": 4, "title": "Create responsive design", "completed": False, "assigned_user_id": "worker2@startupventure.com"}
        ]
    },
    {
        "organization_id": "startup_org_id",
        "collection_id": "onboarding_collection_id",
        "title": "User Onboarding Wizard",
        "description": "Step-by-step onboarding process for new users",
        "status": WorkItemStatus.BACKLOG,
        "priority": WorkItemPriority.MEDIUM,
        "estimated_total_hours": 8.0,
        "estimated_sales_price": 3000.0,
        "estimated_variable_cost": 1000.0,
        "assigned_user_id": "worker2@startupventure.com",  # Startup UI/UX Designer
        "ccr_hours_required": {
            "full_stack_developer": 6.0,
            "founder_review": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Design onboarding flow", "completed": False, "assigned_user_id": "worker2@startupventure.com"},
            {"id": 2, "title": "Create tutorial content", "completed": False, "assigned_user_id": "worker2@startupventure.com"},
            {"id": 3, "title": "Implement progress tracking", "completed": False, "assigned_user_id": "worker1@startupventure.com"}
        ]
    },
    
    # API Integration Project Collection
    {
        "collection_id": "api_integration_collection_id",
        "title": "Payment Gateway Integration",
        "description": "Integrate Stripe payment gateway for processing payments",
        "status": WorkItemStatus.DONE,
        "priority": WorkItemPriority.CRITICAL,
        "estimated_total_hours": 14.0,
        "estimated_sales_price": 10000.0,
        "estimated_variable_cost": 3000.0,
        "ccr_hours_required": {
            "development_team": 12.0,
            "qa_testing": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Set up Stripe account", "completed": True},
            {"id": 2, "title": "Implement payment API", "completed": True},
            {"id": 3, "title": "Add payment UI", "completed": True},
            {"id": 4, "title": "Test payment flow", "completed": True},
            {"id": 5, "title": "Handle error cases", "completed": True}
        ]
    },
    {
        "collection_id": "api_integration_collection_id",
        "title": "Email Service Integration",
        "description": "Integrate SendGrid for transactional emails",
        "status": WorkItemStatus.STANDBY,
        "priority": WorkItemPriority.MEDIUM,
        "estimated_total_hours": 6.0,
        "estimated_sales_price": 3000.0,
        "estimated_variable_cost": 900.0,
        "ccr_hours_required": {
            "development_team": 5.0,
            "devops_pipeline": 1.0
        },
        "tasks": [
            {"id": 1, "title": "Set up SendGrid account", "completed": False},
            {"id": 2, "title": "Implement email templates", "completed": False},
            {"id": 3, "title": "Add email sending logic", "completed": False}
        ]
    },
    
    # Security Audit Implementation Collection
    {
        "collection_id": "security_audit_collection_id",
        "title": "Implement Two-Factor Authentication",
        "description": "Add 2FA support for enhanced account security",
        "status": WorkItemStatus.BACKLOG,
        "priority": WorkItemPriority.HIGH,
        "estimated_total_hours": 10.0,
        "estimated_sales_price": 5000.0,
        "estimated_variable_cost": 1500.0,
        "ccr_hours_required": {
            "development_team": 8.0,
            "qa_testing": 2.0
        },
        "tasks": [
            {"id": 1, "title": "Research 2FA options", "completed": False},
            {"id": 2, "title": "Implement TOTP support", "completed": False},
            {"id": 3, "title": "Add backup codes", "completed": False},
            {"id": 4, "title": "Test 2FA flow", "completed": False}
        ]
    }
]
```

### 📅 Schedules
```python
schedule_definitions = [
    {
        "board_config_id": "main_dev_board_id",
        "capability_channel_id": "development_team_ccr_id",
        "status": ScheduleStatus.PRE_CONSTRAINT,
        "time_unit_position": -2,  # 2 positions before CCR
        "work_item_ids": ["redesign_dashboard_work_item_id"],
        "total_ccr_hours": 12.0
    },
    {
        "board_config_id": "main_dev_board_id", 
        "capability_channel_id": "development_team_ccr_id",
        "status": ScheduleStatus.PRE_CONSTRAINT,
        "time_unit_position": -1,  # 1 position before CCR
        "work_item_ids": ["ios_foundation_work_item_id"],
        "total_ccr_hours": 18.0
    },
    {
        "board_config_id": "qa_testing_board_id",
        "capability_channel_id": "qa_testing_ccr_id", 
        "status": ScheduleStatus.PLANNING,
        "time_unit_position": -3,  # 3 positions before CCR
        "work_item_ids": ["advanced_search_work_item_id"],
        "total_ccr_hours": 2.0
    }
]
```

## Implementation Strategy

### 1. Database Initialization Function Updates
- Extend `init_db()` function in `database.py`
- Add new seed creation functions:
  - `_create_test_ccrs()`
  - `_create_test_board_configs()`
  - `_create_test_collections()`
  - `_create_test_work_items()`
  - `_create_test_schedules()`

### 2. Seed Data Benefits
- **Realistic Testing**: Multiple collections with varying statuses
- **CCR Scenarios**: Different CCR types and capacity constraints
- **Workflow Testing**: Work items in different statuses across the DBR flow
- **Financial Analytics**: Sales prices and costs for throughput calculations
- **Task Management**: Work items with realistic task breakdowns
- **Schedule Testing**: Schedules in different buffer zones
- **Role-based Testing**: Different users owning different collections

### 3. Data Relationships
- All data scoped to "Default Organization"
- CCRs referenced by board configurations
- Collections owned by different users (planner, orgadmin)
- Work items distributed across collections
- Schedules positioned in different buffer zones
- Realistic CCR hour requirements across work items

### 4. Testing Scenarios Enabled
- **Buffer Management**: Schedules in pre/post constraint buffers
- **Capacity Planning**: CCR utilization and bottleneck identification
- **Time Progression**: Advancing schedules through the DBR flow
- **Multi-CCR Workflows**: Work items requiring multiple CCRs
- **Collection Analytics**: Financial and progress tracking
- **Role-based Access**: Different users managing different aspects

## Security Testing Scenarios Enabled

### 🔒 **Multi-Tenant Security Testing**
1. **Organization Isolation**: Users can only see data from their organizations
2. **Cross-Organization Access**: Test users with multiple organization memberships
3. **Access Denial**: Users with no organization membership cannot access any data
4. **Super Admin Override**: Super admin can access all organizations (preserved)

### 👥 **User Access Matrix**
| User | Default Org | TechCorp | StartupVenture | Expected Access |
|------|-------------|----------|----------------|-----------------|
| admin@test.com | ✅ Super Admin | ✅ Super Admin | ✅ Super Admin | All organizations |
| orgadmin@test.com | ✅ Org Admin | ❌ | ❌ | Default Org only |
| planner@test.com | ✅ Planner | ❌ | ❌ | Default Org only |
| worker@test.com | ✅ Worker | ❌ | ❌ | Default Org only |
| worker2@test.com | ✅ Worker | ❌ | ❌ | Default Org only |
| worker3@test.com | ✅ Worker | ❌ | ❌ | Default Org only |
| worker4@test.com | ✅ Worker | ❌ | ❌ | Default Org only |
| worker5@test.com | ✅ Worker | ❌ | ❌ | Default Org only |
| viewer@test.com | ✅ Viewer | ❌ | ❌ | Default Org only |
| admin@techcorp.com | ❌ | ✅ Org Admin | ❌ | TechCorp only |
| planner@techcorp.com | ❌ | ✅ Planner | ❌ | TechCorp only |
| worker1@techcorp.com | ❌ | ✅ Worker | ❌ | TechCorp only |
| worker2@techcorp.com | ❌ | ✅ Worker | ❌ | TechCorp only |
| worker3@techcorp.com | ❌ | ✅ Worker | ❌ | TechCorp only |
| worker4@techcorp.com | ❌ | ✅ Worker | ❌ | TechCorp only |
| founder@startupventure.com | ❌ | ❌ | ✅ Org Admin | StartupVenture only |
| dev@startupventure.com | ❌ | ❌ | ✅ Planner | StartupVenture only |
| worker1@startupventure.com | ❌ | ❌ | ✅ Worker | StartupVenture only |
| worker2@startupventure.com | ❌ | ❌ | ✅ Worker | StartupVenture only |
| consultant@freelance.com | ✅ Worker | ✅ Worker | ❌ | Default + TechCorp |
| contractor@external.com | ❌ | ❌ | ✅ Worker | StartupVenture only |
| outsider@external.com | ❌ | ❌ | ❌ | **NO ACCESS** |
| prospect@potential.com | ❌ | ❌ | ❌ | **NO ACCESS** |

### 🧪 **Critical Security Tests**
1. **Organization Scoping**: Verify work items are filtered by organization_id
2. **Collection Access**: Users can only see collections from their organizations
3. **Schedule Isolation**: Schedules are organization-specific
4. **CCR Visibility**: CCRs are scoped to organizations
5. **Cross-Org Prevention**: Users cannot access other organizations' data
6. **No-Membership Denial**: Users without memberships get empty results
7. **Multi-Org Users**: Consultant can see Default + TechCorp data only

## Database Size Impact
- **Current**: ~15 records (5 users, 5 roles, 1 org, 5 memberships)
- **Proposed Addition**: ~65 records (9 users, 2 orgs, 14 memberships, 9 CCRs, 5 boards, 10 collections, 15+ work items, 5+ schedules)
- **Total**: ~80 records (still very lightweight for development)

## Key Benefits
1. **Comprehensive Security Testing**: Multi-tenant isolation and access control
2. **Realistic Multi-Organization Environment**: 3 organizations with different characteristics
3. **Cross-Organization User Testing**: Users with multiple memberships
4. **Access Denial Testing**: Users with no organization access
5. **Role-based Scenarios**: Different users owning different collections across organizations
6. **DBR Workflow Testing**: Schedules in various buffer positions across organizations
7. **Financial Analytics**: Real sales/cost data for throughput calculations
8. **Multi-CCR Dependencies**: Work items requiring multiple resources
9. **Preserved Existing Tests**: Super Admin credentials unchanged (admin@test.com/admin123)
10. **Scalable**: Comprehensive test environment while remaining lightweight

## Implementation Files to Modify
1. `dbr_mvp/backend/src/dbr/core/database.py` - Add seed functions
2. Test the seed data with existing API endpoints
3. Verify frontend can display the rich test data

This expansion provides a comprehensive testing environment while maintaining the lightweight nature of the MVP.
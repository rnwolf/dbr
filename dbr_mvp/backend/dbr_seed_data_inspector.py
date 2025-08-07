#!/usr/bin/env python3
"""
Enhanced DBR Database Query Script
Displays comprehensive seed data for test scenario development
"""

import sqlite3
import json
from datetime import datetime


def connect_db():
    """Connect to the DBR database"""
    return sqlite3.connect("dbr.db")


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"=== {title.upper()} ===")
    print("=" * 60)


def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")


def query_organizations(cursor):
    """Query and display all organizations"""
    print_section("Organizations")
    cursor.execute("""
        SELECT id, name, description, status, contact_email, country, subscription_level, created_date
        FROM organizations
        ORDER BY name
    """)
    orgs = cursor.fetchall()

    for org in orgs:
        print(f"ID: {org[0]}")
        print(f"Name: {org[1]}")
        print(f"Description: {org[2]}")
        print(f"Status: {org[3]}")
        print(f"Contact: {org[4]}")
        print(f"Country: {org[5]}")
        print(f"Subscription: {org[6]}")
        print(f"Created: {org[7]}")
        print("-" * 40)

    print(f"Total organizations: {len(orgs)}")
    return {org[0]: org[1] for org in orgs}  # Return ID -> Name mapping


def query_roles(cursor):
    """Query and display all roles"""
    print_section("Roles")
    cursor.execute("SELECT id, name, description FROM roles ORDER BY name")
    roles = cursor.fetchall()

    for role in roles:
        print(f"ID: {role[0]}")
        print(f"Name: {role[1]}")
        print(f"Description: {role[2]}")
        print("-" * 40)

    print(f"Total roles: {len(roles)}")
    return {role[0]: role[1] for role in roles}  # Return ID -> Name mapping


def query_users(cursor, role_map):
    """Query and display all users with role information"""
    print_section("Users")
    cursor.execute("""
        SELECT u.id, u.username, u.email, u.display_name, u.active_status,
               u.system_role_id, u.created_date
        FROM users u
        ORDER BY u.email
    """)
    users = cursor.fetchall()

    for user in users:
        role_name = role_map.get(user[5], "Unknown Role")
        print(f"ID: {user[0]}")
        print(f"Username: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Display Name: {user[3]}")
        print(f"Active: {user[4]}")
        print(f"Role: {role_name}")
        print(f"Created: {user[6]}")
        print("-" * 40)

    print(f"Total users: {len(users)}")
    return {user[0]: user[2] for user in users}  # Return ID -> Email mapping


def query_memberships(cursor, org_map, user_map, role_map):
    """Query and display organization memberships"""
    print_section("Organization Memberships")
    cursor.execute("""
        SELECT om.id, om.organization_id, om.user_id, om.role_id,
               om.invitation_status, om.joined_date
        FROM organization_memberships om
        ORDER BY om.organization_id, om.user_id
    """)
    memberships = cursor.fetchall()

    # Group by organization
    org_memberships = {}
    for membership in memberships:
        org_id = membership[1]
        if org_id not in org_memberships:
            org_memberships[org_id] = []
        org_memberships[org_id].append(membership)

    for org_id, members in org_memberships.items():
        org_name = org_map.get(org_id, "Unknown Org")
        print_subsection(f"{org_name} Members")

        for member in members:
            user_email = user_map.get(member[2], "Unknown User")
            role_name = role_map.get(member[3], "Unknown Role")
            print(f"  User: {user_email}")
            print(f"  Role: {role_name}")
            print(f"  Status: {member[4]}")
            print(f"  Joined: {member[5]}")
            print()

    print(f"Total memberships: {len(memberships)}")


def query_ccrs(cursor, org_map):
    """Query and display CCRs"""
    print_section("CCRs (Capacity Constrained Resources)")
    cursor.execute("""
        SELECT id, organization_id, name, description, ccr_type,
               capacity_per_time_unit, time_unit, is_active
        FROM ccrs
        ORDER BY organization_id, name
    """)
    ccrs = cursor.fetchall()

    # Group by organization
    org_ccrs = {}
    for ccr in ccrs:
        org_id = ccr[1]
        if org_id not in org_ccrs:
            org_ccrs[org_id] = []
        org_ccrs[org_id].append(ccr)

    for org_id, ccr_list in org_ccrs.items():
        org_name = org_map.get(org_id, "Unknown Org")
        print_subsection(f"{org_name} CCRs")

        for ccr in ccr_list:
            print(f"  ID: {ccr[0]}")
            print(f"  Name: {ccr[2]}")
            print(f"  Description: {ccr[3]}")
            print(f"  Type: {ccr[4]}")
            print(f"  Capacity: {ccr[5]} {ccr[6]}")
            print(f"  Active: {ccr[7]}")
            print()

    print(f"Total CCRs: {len(ccrs)}")


def query_collections(cursor, org_map, user_map):
    """Query and display collections (if any exist)"""
    print_section("Collections")
    cursor.execute("""
        SELECT id, organization_id, name, description, status, owner_user_id,
               estimated_sales_price, estimated_variable_cost, url
        FROM collections
        ORDER BY organization_id, name
    """)
    collections = cursor.fetchall()

    if not collections:
        print("No collections found (stub implementation)")
        return

    # Group by organization
    org_collections = {}
    for collection in collections:
        org_id = collection[1]
        if org_id not in org_collections:
            org_collections[org_id] = []
        org_collections[org_id].append(collection)

    for org_id, coll_list in org_collections.items():
        org_name = org_map.get(org_id, "Unknown Org")
        print_subsection(f"{org_name} Collections")

        for coll in coll_list:
            owner_email = (
                user_map.get(coll[5], "Unknown Owner") if coll[5] else "No Owner"
            )
            throughput = (coll[6] or 0) - (coll[7] or 0)
            print(f"  ID: {coll[0]}")
            print(f"  Name: {coll[2]}")
            print(f"  Description: {coll[3]}")
            print(f"  Status: {coll[4]}")
            print(f"  Owner: {owner_email}")
            print(
                f"  Sales Price: ${coll[6]:,.2f}" if coll[6] else "  Sales Price: $0.00"
            )
            print(
                f"  Variable Cost: ${coll[7]:,.2f}"
                if coll[7]
                else "  Variable Cost: $0.00"
            )
            print(f"  Throughput: ${throughput:,.2f}")
            print(f"  URL: {coll[8]}")
            print()

    print(f"Total collections: {len(collections)}")


def query_work_items(cursor, org_map, user_map):
    """Query and display work items (if any exist)"""
    print_section("Work Items")
    cursor.execute("""
        SELECT id, organization_id, collection_id, title, description, status,
               priority, estimated_total_hours, estimated_sales_price,
               estimated_variable_cost, tasks
        FROM work_items
        ORDER BY organization_id, collection_id, title
    """)
    work_items = cursor.fetchall()

    if not work_items:
        print("No work items found (stub implementation)")
        return

    for item in work_items:
        org_name = org_map.get(item[1], "Unknown Org")
        throughput = (item[8] or 0) - (item[9] or 0)

        print(f"ID: {item[0]}")
        print(f"Organization: {org_name}")
        print(f"Collection ID: {item[2]}")
        print(f"Title: {item[3]}")
        print(f"Description: {item[4]}")
        print(f"Status: {item[5]}")
        print(f"Priority: {item[6]}")
        print(f"Estimated Hours: {item[7]}")
        print(f"Sales Price: ${item[8]:,.2f}" if item[8] else "Sales Price: $0.00")
        print(f"Variable Cost: ${item[9]:,.2f}" if item[9] else "Variable Cost: $0.00")
        print(f"Throughput: ${throughput:,.2f}")

        # Parse and display tasks if they exist
        if item[10]:
            try:
                tasks = json.loads(item[10])
                print(f"Tasks ({len(tasks)}):")
                for task in tasks:
                    status = "✓" if task.get("completed", False) else "○"
                    print(f"  {status} {task.get('title', 'Untitled Task')}")
            except json.JSONDecodeError:
                print("Tasks: Invalid JSON format")
        else:
            print("Tasks: None")

        print("-" * 40)

    print(f"Total work items: {len(work_items)}")


def generate_test_credentials():
    """Generate a summary of test credentials for easy reference"""
    print_section("Test Credentials Summary")

    credentials = [
        ("admin@test.com", "admin123", "Super Admin", "All organizations"),
        (
            "orgadmin@test.com",
            "orgadmin123",
            "Organization Admin",
            "Default Organization only",
        ),
        ("planner@test.com", "planner123", "Planner", "Default Organization only"),
        ("worker@test.com", "worker123", "Worker", "Default Organization only"),
        (
            "worker2@test.com",
            "default123",
            "Worker (Frontend)",
            "Default Organization only",
        ),
        (
            "worker3@test.com",
            "default123",
            "Worker (Backend)",
            "Default Organization only",
        ),
        ("worker4@test.com", "default123", "Worker (QA)", "Default Organization only"),
        (
            "worker5@test.com",
            "default123",
            "Worker (DevOps)",
            "Default Organization only",
        ),
        ("viewer@test.com", "viewer123", "Viewer", "Default Organization only"),
        (
            "admin@techcorp.com",
            "techcorp123",
            "Organization Admin",
            "TechCorp Solutions only",
        ),
        ("planner@techcorp.com", "techcorp123", "Planner", "TechCorp Solutions only"),
        (
            "worker1@techcorp.com",
            "techcorp123",
            "Worker (Senior Dev)",
            "TechCorp Solutions only",
        ),
        (
            "worker2@techcorp.com",
            "techcorp123",
            "Worker (Frontend)",
            "TechCorp Solutions only",
        ),
        (
            "worker3@techcorp.com",
            "techcorp123",
            "Worker (Backend)",
            "TechCorp Solutions only",
        ),
        (
            "worker4@techcorp.com",
            "techcorp123",
            "Worker (QA)",
            "TechCorp Solutions only",
        ),
        (
            "founder@startupventure.com",
            "startup123",
            "Organization Admin",
            "StartupVenture Inc only",
        ),
        ("dev@startupventure.com", "startup123", "Planner", "StartupVenture Inc only"),
        (
            "worker1@startupventure.com",
            "startup123",
            "Worker (Full-Stack)",
            "StartupVenture Inc only",
        ),
        (
            "worker2@startupventure.com",
            "startup123",
            "Worker (UI/UX)",
            "StartupVenture Inc only",
        ),
        (
            "consultant@freelance.com",
            "consultant123",
            "Worker",
            "Default + TechCorp (Multi-org)",
        ),
        (
            "contractor@external.com",
            "contractor123",
            "Worker",
            "StartupVenture Inc only",
        ),
        (
            "outsider@external.com",
            "outsider123",
            "Viewer",
            "NO ACCESS (No memberships)",
        ),
        (
            "prospect@potential.com",
            "prospect123",
            "Viewer",
            "NO ACCESS (No memberships)",
        ),
    ]

    print("Email | Password | Role | Access")
    print("-" * 80)
    for email, password, role, access in credentials:
        print(f"{email:<30} | {password:<12} | {role:<20} | {access}")


def main():
    """Main function to run all queries"""
    print("DBR Database Seed Data Analysis")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Query all data with relationships
        org_map = query_organizations(cursor)
        role_map = query_roles(cursor)
        user_map = query_users(cursor, role_map)
        query_memberships(cursor, org_map, user_map, role_map)
        query_ccrs(cursor, org_map)
        query_collections(cursor, org_map, user_map)
        query_work_items(cursor, org_map, user_map)
        generate_test_credentials()

        print_section("Summary")
        print(f"Organizations: {len(org_map)}")
        print(f"Roles: {len(role_map)}")
        print(f"Users: {len(user_map)}")
        print(f"Multi-tenant security testing: READY")
        print(f"Cross-organization access testing: READY")
        print(f"Role-based permission testing: READY")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

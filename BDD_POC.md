# BDD Proof Of Concept

Successfully completed.

Outcome:


Develop FastAPI endpoints.
Update SpeakEasy generated SDK from OpenAPI generated file from FastAPI endpoints.
Develop BDD feature scenarios
Develop BDD tests to validate that FastAPI provides services required
Develop TKinter based GUI for services
Test services with users
Harden and extend services
Enhance with additional web and mobile frontend features.


## POC Plan

We are developing a POC of Behaviour Driven Development, (BDD) testing for this project using the SDK because doing TDD via the TKinter GUI app was proving to be rather brittle.

The BDD tests are in C:\Users\rnwol\workspace\dbr\dbr_mvp\frontend\tests_bdd

While creating the BDD tests there where many occations on which the test where created with non-existant method calls.
The file tmp_rovodev_sdk_methods_reference.md is a comprehensive SDK reference of the SDK methods.

Looking at this, several critical errors where spotted:

🎯 Key Issues spotted:

 1. Work Items: I was using get() but should use list()                                                               │
 2. Schedules: I was using get() but should use list()                                                                │
 3. Users: I was missing the required organization_id parameter                                                       │
 4. Method names: I had some wrong method names                                                                       │

Fix the BDD test with the correct SDK method calls:


The debugging shows:

  1. Organizations API returns empty list - No organizations exist or are accessible                                   │
  2. Admin user can't create organizations - Permission denied (403)                                                   │
  3. Admin user lacks Super Admin role - The user exists but doesn't have the right permissions                        │

This suggests that either:                                                                                           │

 • The database initialization didn't run properly, or                                                               │
 • The admin user wasn't assigned the Super Admin role correctly                                                     │

 Let me help you check and fix this. Based on your DBR_TEST_DATA_AND_CREDENTIALS.md, there should be a "Default       │
 Organization" and the admin user should be a Super Admin.                                                            │

Let's Check Your Database                                             │

Can you run this command to check what's actually in your database?                                                  │

│  cd dbr_mvp/backend                                                                                                  │
│  # Check if the database file exists                                                                                 │
│  ls -la dbr.db                                                                                                       │

# Check what's in the organizations table
uv run python -c "
import sqlite3
conn = sqlite3.connect('dbr.db')
cursor = conn.cursor()
print('=== ORGANIZATIONS ===')
cursor.execute('SELECT id, name, status FROM organizations')
orgs = cursor.fetchall()
for org in orgs:
    print(f'ID: {org[0]}, Name: {org[1]}, Status: {org[2]}')
print(f'Total organizations: {len(orgs)}')

print('\n=== USERS ===')
cursor.execute('SELECT id, username, email, system_role_id FROM users WHERE username = \"admin\"')
admin = cursor.fetchone()
if admin:
    print(f'Admin User - ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Role ID: {admin[3]}')
else:
    print('No admin user found')

print('\n=== ROLES ===')
cursor.execute('SELECT id, name FROM roles')
roles = cursor.fetchall()
for role in roles:
    print(f'Role ID: {role[0]}, Name: {role[1]}')

conn.close()
"

🎯 Expected Results                                                  │

│ If the database is properly initialized, you should see:                                                             │

 • At least one organization (Default Organization)                                                                  │
 • The admin user with a Super Admin role ID                                                                         │
 • All 5 system roles defined                                                                                        │

🔧 If Database is Empty or Incomplete                                         │

If the database isn't properly set up, you can reinitialize it:                                                      │

│  cd dbr_mvp/backend                                                                                                  │
│  # Delete the existing database                                                                                      │
│  rm dbr.db                                                                                                           │

│  # Restart the backend (this should trigger database initialization)                                                 │

 uv run uvicorn dbr.main:app --host 127.0.0.1 --port 8002                                                            │

Please run the database check command and share the output. This will tell us exactly what's missing and how to fix  │
it!                                                                                                                  │
                                                                                                                      │
This is a perfect example of how BDD testing helps us discover real infrastructure and setup issues that would be    │
hidden by GUI mocking.

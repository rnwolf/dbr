Feature: Work Item Management
  As a user with appropriate permissions,
  I want to manage work items in the DBR system,
  so that I can control the flow of work through our capacity constrained resources.

  Background:
    Given a running backend server
    And an authenticated planner user
    And a default organization exists

  Scenario: Create a work item as Planner
    When I create a work item with title "Implement user authentication", description "Add JWT-based authentication", priority "high"
    Then the work item should be created successfully
    And the work item should have status "Backlog"
    And the work item should be assigned to my organization

  Scenario: Create a work item with collection assignment
    Given a collection exists in the organization
    When I create a work item with title "Feature Development", collection assignment, estimated hours 16
    Then the work item should be created successfully
    And the work item should be assigned to the collection
    And the work item should have the correct estimated hours

  Scenario: List work items by status
    Given there are work items with various statuses
    When I request work items with status "Ready"
    Then I should receive only work items with "Ready" status
    And all work items should belong to my organization

  Scenario: Update work item status as Planner
    Given a work item exists with status "Ready"
    When I update the work item status to "In-Progress"
    Then the work item status should be updated successfully
    And the work item should appear in "In-Progress" lists

  Scenario: Add tasks to work item
    Given a work item exists
    When I add a task "Write unit tests" with estimated hours 4
    Then the task should be added to the work item
    And the work item should include the new task in its task list

  Scenario: Work item priority management
    Given multiple work items exist with different priorities
    When I request work items sorted by priority
    Then work items should be returned in priority order
    And critical priority items should appear first

  Scenario: Organization Admin can manage work items
    Given I am authenticated as an organization admin user
    When I create a work item with title "Admin Work Item", description "Created by admin", priority "medium"
    Then the work item should be created successfully
    And when I update the work item priority to "high"
    Then the work item should be updated successfully
    And when I delete the work item
    Then the work item should be deleted successfully

  Scenario: Worker can view and update assigned work items
    Given I am authenticated as a worker user
    And work items exist in the organization
    And a work item is assigned to me
    When I request the list of work items
    Then I should receive a list of work items
    And when I update my assigned work item status to "In-Progress"
    Then the work item status should be updated successfully
    But when I try to create a new work item
    Then I should receive a permission denied error
    And when I try to delete an existing work item
    Then I should receive a permission denied error

  Scenario: Worker can update tasks on assigned work items
    Given I am authenticated as a worker user
    And a work item is assigned to me with tasks
    When I update a task status to "Completed"
    Then the task should be updated successfully
    And when I update task actual hours to 6
    Then the task actual hours should be updated

  Scenario: Viewer can only view work items
    Given I am authenticated as a viewer user
    And work items exist in the organization
    When I request the list of work items
    Then I should receive a list of work items
    But when I try to create a new work item
    Then I should receive a permission denied error
    And when I try to update an existing work item
    Then I should receive a permission denied error
    And when I try to delete an existing work item
    Then I should receive a permission denied error

  Scenario: Work items are scoped by organization
    Given there are work items in multiple organizations
    When I request work items for my organization
    Then I should only see work items from my organization
    And I should not see work items from other organizations

  Scenario: Filter work items by collection
    Given there are work items in different collections
    When I request work items for a specific collection
    Then I should receive only work items from that collection
    And all returned work items should belong to my organization

  Scenario: Filter work items by priority
    Given there are work items with various priorities
    When I request work items with priority "high"
    Then I should receive only work items with "high" priority
    And all returned work items should belong to my organization

  Scenario: Filter work items by responsible user
    Given there are work items assigned to different users
    When I request work items assigned to a specific user
    Then I should receive only work items assigned to that user
    And all returned work items should belong to my organization

  Scenario: Work item with CCR hours requirements
    When I create a work item with title "Complex Feature", CCR hours "development: 12, testing: 4, design: 2"
    Then the work item should be created successfully
    And the work item should have the correct CCR hours breakdown
    And the total estimated hours should be calculated correctly

  Scenario: Work item with financial information
    When I create a work item with title "Revenue Feature", estimated sales price 50000, estimated variable cost 10000
    Then the work item should be created successfully
    And the work item should have the correct financial information
    And the estimated profit should be calculated correctly

  Scenario: Work item with due date
    When I create a work item with title "Time-critical Feature", due date "2024-12-31T23:59:59Z"
    Then the work item should be created successfully
    And the work item should have the correct due date

  Scenario: Update work item collection assignment
    Given a work item exists without collection assignment
    And a collection exists in the organization
    When I update the work item to assign it to the collection
    Then the work item should be updated successfully
    And the work item should be assigned to the collection

  Scenario: Work item status workflow validation
    Given a work item exists with status "Backlog"
    When I update the work item status to "Ready"
    Then the work item status should be updated successfully
    And when I update the work item status to "In-Progress"
    Then the work item status should be updated successfully
    And when I update the work item status to "Done"
    Then the work item status should be updated successfully
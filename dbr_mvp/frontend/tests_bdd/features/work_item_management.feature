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
    When I create a work item with title "Feature Development", collection assignment, and estimated hours 16
    Then the work item should be created successfully
    And the work item should be assigned to the collection

  Scenario: Filter work items by collection
    Given there are work items in different collections
    When I request work items for a specific collection
    Then I should receive only work items from that collection

  Scenario: List work items by status
    Given there are work items with various statuses
    When I request work items with status "Ready"
    Then I should receive only work items with "Ready" status
    And all work items should belong to my organization

  Scenario: Add tasks to a work item
    Given a work item exists
    When I add a task "Develop API endpoint" with estimated hours 8
    And I add a task "Write unit tests" with estimated hours 4
    Then the tasks should be added to the work item
    And the work item should include the new tasks in its task list

  Scenario: Work item priority management
    Given multiple work items exist with different priorities
    When I request work items sorted by priority
    Then work items should be returned in priority order
    And critical priority items should appear first

  Scenario: Work items are scoped by organization
    Given there are work items in multiple organizations
    When I request work items for my organization
    Then I should only see work items from my organization
    And I should not see work items from other organizations

  Scenario: Assign a work item to a specific user
    Given a "worker" user exists in the organization
    When I create a work item with title "Task for Worker" and assign it to the "worker" user
    Then the work item should be created successfully
    And the work item should be assigned to the "worker" user

  Scenario: Create a work item with an associated URL
    When I create a work item with title "Docs Task" and URL "https://example.com/docs/task-123"
    Then the work item should be created successfully
    And the work item should have the URL "https://example.com/docs/task-123"

  Scenario: Verify creation and update timestamps
    When I create a work item with title "Timestamp Test"
    Then the work item should have a valid creation timestamp
    And the updated timestamp should match the creation timestamp
    When I update the work item's description to "new description"
    Then the work item's updated timestamp should be later than its creation timestamp

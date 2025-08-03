Feature: Work Item Management
  As a Planner,
  I want to manage work items in the DBR system,
  so that I can control the flow of work through our capacity constrained resources.

  Background:
    Given a running backend server
    And an authenticated planner user
    And a default organization exists

  Scenario: Create a work item
    When I create a work item with title "Implement user authentication", description "Add JWT-based authentication", priority "high"
    Then the work item should be created successfully
    And the work item should have status "Backlog"
    And the work item should be assigned to my organization

  Scenario: List work items by status
    Given there are work items with various statuses
    When I request work items with status "Ready"
    Then I should receive only work items with "Ready" status
    And all work items should belong to my organization

  Scenario: Update work item status
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
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

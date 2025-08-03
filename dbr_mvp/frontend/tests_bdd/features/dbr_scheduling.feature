Feature: DBR Scheduling and Time Progression
  As a Planner,
  I want to create schedules and advance time in the DBR system,
  so that I can manage the flow of work through capacity constrained resources.

  Background:
    Given a running backend server
    And an authenticated planner user
    And a default organization with board configuration exists
    And work items are available for scheduling

  Scenario: Create a schedule with work items
    When I create a schedule with selected work items
    Then the schedule should be created successfully
    And the schedule should contain the selected work items
    And the schedule should have status "Planning"
    And the total CCR hours should be calculated correctly

  Scenario: Advance time unit
    Given schedules exist in various statuses
    When I advance the system time by one unit
    Then all schedules should progress through their workflow
    And schedules in "Pre-Constraint" should move toward the CCR
    And completed schedules should be marked as "Completed"
    And the system time should be incremented

  Scenario: Schedule analytics
    Given a completed schedule exists
    When I request analytics for the schedule
    Then I should receive performance metrics
    And the analytics should include throughput data
    And the analytics should include buffer status information

  Scenario: Board analytics
    Given multiple schedules exist for a board
    When I request board-level analytics
    Then I should receive aggregated performance data
    And the analytics should show overall system health
    And the analytics should identify bottlenecks

  Scenario: Schedule capacity validation
    Given a board configuration with CCR capacity limits
    When I attempt to create a schedule that exceeds CCR capacity
    Then the system should validate capacity constraints
    And I should receive appropriate warnings or errors
    And the schedule should not be created if it violates constraints
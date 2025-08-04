Feature: Collection Management
  As a Planner or Organization Admin,
  I want to manage collections (projects, epics, releases) in the DBR system,
  so that I can organize work items into logical groups.

  Background:
    Given a running backend server
    And an authenticated planner user
    And a default organization exists

  @investigate
  Scenario: Create a new collection
    When I create a collection with name "Q4 Product Release", description "Major product release for Q4", type "Release"
    Then the collection should be created successfully
    And the collection should have status "planning"
    And the collection should be assigned to my organization

  @investigate
  Scenario: List collections by type
    Given there are collections with various types
    When I request collections with type "Project"
    Then I should receive only collections with "Project" type
    And all collections should belong to my organization

  Scenario: Update collection status
    Given a collection exists with status "planning"
    When I update the collection status to "active"
    Then the collection status should be updated successfully
    And the collection should appear in "active" status lists

  Scenario: Worker can view but not modify collections
    Given I am authenticated as a worker user
    And collections exist in the organization
    When I request the list of collections
    Then I should receive a list of collections
    But when I try to create a new collection
    Then I should receive a permission denied error
    And when I try to update an existing collection
    Then I should receive a permission denied error

  Scenario: Viewer can only view collections
    Given I am authenticated as a viewer user
    And collections exist in the organization
    When I request the list of collections
    Then I should receive a list of collections
    But when I try to create a new collection
    Then I should receive a permission denied error
    And when I try to update an existing collection
    Then I should receive a permission denied error
    And when I try to delete an existing collection
    Then I should receive a permission denied error

  Scenario: Organization Admin can manage collections
    Given I am authenticated as an organization admin user
    When I create a collection with name "Admin Collection", description "Created by admin", type "Epic"
    Then the collection should be created successfully
    And when I update the collection name to "Updated Admin Collection"
    Then the collection should be updated successfully
    And when I delete the collection
    Then the collection should be deleted successfully

  Scenario: Collections are scoped by organization
    Given there are collections in multiple organizations
    When I request collections for my organization
    Then I should only see collections from my organization
    And I should not see collections from other organizations

  Scenario: Filter collections by status
    Given there are collections with various statuses
    When I request collections with status "active"
    Then I should receive only collections with "active" status
    And all returned collections should belong to my organization

  Scenario: Collection with financial information
    When I create a collection with name "Revenue Project", estimated sales price 100000, estimated variable cost 25000
    Then the collection should be created successfully
    And the collection should have the correct financial information
    And the estimated profit should be calculated correctly

  Scenario: Collection with target completion date
    When I create a collection with name "Time-bound Project", target completion date "2024-12-31T23:59:59Z", timezone "Europe/London"
    Then the collection should be created successfully
    And the collection should have the correct target completion date
    And the timezone should be properly stored
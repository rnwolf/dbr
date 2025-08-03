Feature: User Management
  As an Organization Admin,
  I want to manage users in my organization,
  so that I can control access and assign appropriate roles.

  Background:
    Given a running backend server
    And an authenticated organization admin user

  Scenario: Create a new user
    When I create a new user with username "newuser", email "newuser@example.com", display name "New User" and role "Planner"
    Then the user should be created successfully
    And the user should appear in the organization's user list
    And the user should have the "Planner" role assigned

  Scenario: List organization users
    Given there are existing users in the organization
    When I request the list of users for my organization
    Then I should receive a list of users
    And each user should have valid user information
    And users should be filtered by my organization

  Scenario: Update user role
    Given a user "testuser" exists with role "Worker"
    When I update the user's role to "Planner"
    Then the user's role should be updated successfully
    And the user should have "Planner" permissions

  Scenario: Deactivate user
    Given an active user "testuser" exists
    When I deactivate the user
    Then the user should be marked as inactive
    And the user should not be able to authenticate
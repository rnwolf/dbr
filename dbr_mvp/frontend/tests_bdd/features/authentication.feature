Feature: User Authentication
  As a user,
  I want to authenticate with the DBR system,
  so that I can access my organization's data.

  Scenario: Successful Authentication
    Given a running backend server
    And a registered user with username "testuser_bdd", password "password", email "testuser_bdd@example.com" and display name "Test User BDD"
    When the user authenticates with username "testuser_bdd" and password "password"
    Then the user should receive an access token
    And the user information should be retrieved successfully
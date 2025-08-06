Feature: Organization Management
  As a Super Admin
  I want to manage organizations in the DBR system
  So that I can control multi-tenant access and configuration

  Background:
    Given a running backend server
    And an authenticated super admin user

  Scenario: Create a new organization
    When I create a new organization with name "Test Corp", description "A test corporation", contact email "admin@testcorp.com" and country "GB"
    Then the organization should be created successfully
    And the organization should have status "active"
    And the organization should have the correct details

  Scenario: List all organizations
    Given multiple organizations exist in the system
    When I request the list of all organizations
    Then I should receive a list of organizations
    And each organization should have valid organization information
    And organizations should be properly structured

  Scenario: Get organization by ID
    Given an organization "Example Org" exists
    When I request the organization details by ID
    Then I should receive the organization information
    And the organization details should match the expected values

  Scenario: Update organization information
    Given an organization "Updatable Org" exists
    When I update the organization's name to "Updated Organization" and description to "Updated description"
    Then the organization should be updated successfully
    And the organization should reflect the new information

  Scenario: Delete organization
    Given an organization "Deletable Org" exists with no dependencies
    When I delete the organization
    Then the organization should be deleted successfully
    And the organization should no longer exist in the system

  Scenario: Organization subscription level management
    Given an organization "Subscription Org" exists
    When I update the organization subscription level to "premium"
    Then the organization subscription should be updated successfully

  Scenario: Multi-tenant isolation
    Given multiple organizations "Org A" and "Org B" exist
    And each organization has its own users and data
    When I access data from "Org A" as an "Org A" user
    Then I should only see data belonging to "Org A"
    And I should not have access to "Org B" data

  Scenario: Organization settings and preferences
    Given an organization "Settings Org" exists
    When I update the organization's timezone to "America/New_York"
    Then the organization settings should be saved successfully

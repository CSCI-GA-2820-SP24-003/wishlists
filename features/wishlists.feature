Feature: The Wishlist service back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my Wishlists

Background:
    Given the following wishlists
        | id | username | name          | is_public | description        |
        | 2  | user2    | Wish List     | False     | Private wishlist   |
        | 3  | user3    | My Wish List  | False     | Private wishlist   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I set the "Name" to "wishlist 1"
    And I select "True" in the "Is Public" dropdown
    And I set the "Description" to "description 1"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "ID" field should be empty
    And the "Username" field should be empty
    And the "Name" field should be empty
    And the "description" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "user1" in the "Username" field
    And I should see "wishlist 1" in the "Name" field
    And I should see "True" in the "Is Public" dropdown
    And I should see "description 1" in the "Description" field
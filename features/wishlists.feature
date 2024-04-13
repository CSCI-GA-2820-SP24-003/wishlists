Feature: The wishlist service back-end
    As a a Wishlist Manager
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | username    | name          |
        | user1       | wishlist_1    |
        | user1       | wishlist_2    |
        | user2       | wishlist_3    |
        | user3       | wishlist_4    |
        | user4       | wishlist_5    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists RESTful Service" in the title
    And I should not see "404 Not Found"
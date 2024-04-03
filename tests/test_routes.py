"""
Wishlist API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from datetime import datetime, timezone, timedelta
from wsgi import app
from service.common import status
from service.models import db, Wishlist, WishlistItem
from .factories import WishlistFactory, WishlistItemFactory

# cspell: ignore psycopg testdb, idempotency

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class WishlistService(TestCase):
    """REST API Server Tests"""

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    # pylint: disable=duplicate-code
    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    # pylint: disable=duplicate-code
    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishlistItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists

    ######################################################################
    #  W I S H L I S T   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist_and_duplicate(self):
        """It should create a new wishlist and prevent creating a duplicate"""

        # First, create a wishlist
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "Failed to create a wishlist")

        # Verify the location header is set
        location = resp.headers.get("Location")
        self.assertIsNotNone(location, "Location header is missing")

        # Verify the wishlist data
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names do not match")
        self.assertEqual(new_wishlist["description"], wishlist.description, "Descriptions do not match")
        self.assertEqual(new_wishlist["username"], wishlist.username, "Usernames do not match")
        self.assertEqual(new_wishlist["is_public"], wishlist.is_public, "is_public flag does not match")

        # Check created_at and last_updated_at timing
        current_time = datetime.now(timezone.utc)
        created_at = datetime.fromisoformat(new_wishlist["created_at"]).replace(tzinfo=timezone.utc)
        last_updated_at = datetime.fromisoformat(new_wishlist["last_updated_at"]).replace(tzinfo=timezone.utc)

        tolerance = timedelta(seconds=1)
        self.assertTrue(abs(created_at - current_time) <= tolerance, "Created_at timestamp is not as expected")
        self.assertTrue(abs(last_updated_at - current_time) <= tolerance, "Last_updated_at timestamp is not as expected")

        # Attempt to create a duplicate wishlist
        duplicate_resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        # Expecting a 409 Conflict status code for a duplicate
        self.assertEqual(duplicate_resp.status_code, status.HTTP_409_CONFLICT, "Duplicate wishlist was unexpectedly created")

    # def test_create_wishlist(self):
    #     """It should create a new wishlist"""

    #     wishlist = WishlistFactory()
    #     resp = self.client.post(
    #         BASE_URL, json=wishlist.serialize(), content_type="application/json"
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # Make sure location header is set
    #     location = resp.headers.get("Location", None)
    #     self.assertIsNotNone(location)

    #     # Check the data is correct
    #     new_wishlist = resp.get_json()
    #     self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
    #     self.assertEqual(
    #         new_wishlist["description"],
    #         wishlist.description,
    #         "Description does not match",
    #     )
    #     self.assertEqual(
    #         new_wishlist["username"], wishlist.username, "Username does not match"
    #     )
    #     self.assertEqual(
    #         new_wishlist["is_public"], wishlist.is_public, "IsPublic does not match"
    #     )
    #     current_time = datetime.now(timezone.utc)

    #     created_at = datetime.fromisoformat(new_wishlist["created_at"]).replace(
    #         tzinfo=timezone.utc
    #     )
    #     last_updated_at = datetime.fromisoformat(
    #         new_wishlist["last_updated_at"]
    #     ).replace(tzinfo=timezone.utc)

    #     # Check that created_at and last_updated_at are within a certain tolerance (e.g., 1 second)
    #     tolerance = timedelta(seconds=1)
    #     self.assertTrue(
    #         abs(created_at - current_time) <= tolerance,
    #         f"Created at time '{created_at}' is not close to current time '{current_time}'",
    #     )
    #     self.assertTrue(
    #         abs(last_updated_at - current_time) <= tolerance,
    #         f"Last updated at time '{last_updated_at}' is not close to current time '{current_time}'",
    #     )
    #     # self.assertEqual(
    #     #     new_wishlist["created_at"],
    #     #     wishlist.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    #     #     "Created at date does not match",
    #     # )

    #     # self.assertEqual(
    #     #     new_wishlist["last_updated_at"],
    #     #     wishlist.last_updated_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    #     #     "Last updated date does not match",
    #     # )

    def test_update_wishlist(self):
        """It should Update an existing Wishlist"""
        # create a Wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=test_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the Wishlist
        new_wishlist = resp.get_json()
        new_wishlist["name"] = "Birthday wishlist"
        new_wishlist_id = new_wishlist["id"]
        resp = self.client.put(f"{BASE_URL}/{new_wishlist_id}", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "Birthday wishlist")
        self.assertEqual(updated_wishlist["created_at"], new_wishlist["created_at"])

    def test_update_nonexisting_wishlist(self):
        """It should Not be able to Update a non-existing Wishlist"""
        # create a non-existing Wishlist to update

        test_wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=test_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the non-existing Wishlist
        non_existing_wishlist = resp.get_json()
        non_existing_wishlist["name"] = "Birthday wishlist"
        new_wishlist_id = non_existing_wishlist["id"] + 1
        resp = self.client.put(
            f"{BASE_URL}/{new_wishlist_id}", json=non_existing_wishlist
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist(self):
        """It should Delete an existing wishlist"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existent_wishlist(self):
        """It should be able to appropriate status code if record cannot not found"""
        dummy_id = 0
        resp = self.client.delete(f"{BASE_URL}/{dummy_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_check_content_type(self):
        """It should check the content type"""
        wishlist_dict = {
            "name": "test wishlist",
            "description": "test description",
            "username": "testuser",
            "is_public": False,
            "created_at": "2024-02-27 00:00:00",
            "last_updated_at": "2024-02-27 00:00:00",
        }
        resp = self.client.post(
            "/wishlists",
            query_string=wishlist_dict,
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        resp = self.client.post(
            "/wishlists",
            data=wishlist_dict,
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_list_wishlists(self):
        """It should Get a list of Wishlists"""
        self._create_wishlists(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  I T E M   T E S T   C A S E S   H E R E
    ######################################################################

    def test_add_item(self):
        """It should Add an item to a wishlist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["product_description"], item.product_description)
        self.assertEqual(float(data["product_price"]), float(item.product_price))

    def test_add_items_in_invalid_wishlist(self):
        """It should not be able to add an item in invalid wishlists"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        wishlist_id = wishlist.id + 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_wishlist_items(self):
        """It should Get a list of Addresses"""
        # add two addresses to account
        wishlist = self._create_wishlists(1)[0]
        items_list = WishlistItemFactory.create_batch(2)

        # Create address 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items", json=items_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create address 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items", json=items_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_list_invalid_wishlists_items(self):
        """It should not get a list of items from an invalid wishlists"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wishlist_id = wishlist.id + 1
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_item(self):
        """It should read an item from wishlist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["product_description"], item.product_description)
        self.assertEqual(float(data["product_price"]), float(item.product_price))

    def test_read_non_existent_item(self):
        """It should not be able to read a non-existent item"""

        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # Case 1 : Wishlist does not exist
        dummy_wishlist_id = -10
        resp = self.client.get(
            f"{BASE_URL}/{dummy_wishlist_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Case 2 : Item does not exist
        dummy_item_id = -10
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{dummy_item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_item_with_incorrect_wishlist_id(self):
        """It should not be able to read an existent item if wishlist_id provided is wrong"""
        wishlist = self._create_wishlists(1)[0]
        wishlist2 = self._create_wishlists(1)[0]
        self.assertNotEqual(wishlist.id, wishlist2.id)
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist2.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist(self):
        """It should Read a single wishlist"""
        # get the id of a wishlist
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], wishlist.name)
        self.assertEqual(data["id"], wishlist.id)

    def test_get_wishlist_not_found(self):
        """It should not Read a wishlist that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist_item(self):
        """It should Delete a wishlist item from the wishlist if it exists"""
        # get the id of an wishlist
        wishlist = self._create_wishlists(1)[0]
        wishlist_item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        wishlist_item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id}/items/{wishlist_item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{wishlist_item_id}",
            content_type="application/json",
        )

    def test_update_wishlist_item(self):
        """It should Update an item on a wishlist"""
        # create a item inside a wishlist
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["product_description"] = ".."  # change the product description
        # update the item in the database
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # retrieve the updated item
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_description"], "..")

    def test_update_non_existing_wishlist_item(self):
        """It should not Update an non-existing item on a wishlist"""
        # create a item and wishlist
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Case 1: Wishlist does not exist
        data = resp.get_json()
        logging.debug(data)
        wishlist_id = wishlist.id + 1
        item_id = data["id"]
        resp = self.client.put(
            f"{BASE_URL}/{wishlist_id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Case 2: Item does not exist in the wishlist
        item_id = item_id + 1
        data["product_description"] = ".."
        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_with_incorrect_wishlist_id(self):
        """It should not be able to update an existent item if wishlist_id provided is wrong"""
        wishlist = self._create_wishlists(1)[0]
        wishlist2 = self._create_wishlists(1)[0]
        self.assertNotEqual(wishlist.id, wishlist2.id)
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["product_description"] = ".."

        # update the item
        resp = self.client.put(
            f"{BASE_URL}/{wishlist2.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  A C T I O N   R O U T E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_publish_wishlist(self):
        """It should publish a wishlist"""
        wishlist = WishlistFactory()
        wishlist.is_public = False
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        wishlist_id = wishlist.id

        resp = self.client.put(f"{BASE_URL}/{wishlist_id}/publish")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], wishlist_id)
        self.assertEqual(data["is_public"], True)

        # testing idempotency
        resp2 = self.client.put(f"{BASE_URL}/{wishlist_id}/publish")

        self.assertEqual(data, resp2.get_json())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_publish_wishlist_for_non_existent_wishlist(self):
        """It should return 404 status code when publishing a wishlist that does not exist"""
        resp = self.client.put(f"{BASE_URL}/99999/publish")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist_by_name(self):
        """It should Get a Wishlist by Name"""
        wishlists = self._create_wishlists(3)
        resp = self.client.get(BASE_URL, query_string=f"name={wishlists[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], wishlists[1].name)

    def test_get_wishlist_by_username(self):
        """It should Get a Wishlist by Username"""
        wishlists = self._create_wishlists(3)
        resp = self.client.get(
            BASE_URL, query_string=f"username={wishlists[1].username}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["username"], wishlists[1].username)

    def test_get_wishlist_items_by_product_name(self):
        """It should Get a Wishlist Items by Product name"""

        wishlist = self._create_wishlists(1)[0]
        items_list = WishlistItemFactory.create_batch(5)

        for item in items_list:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items", json=item.serialize()
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        item_1_name = items_list[1].product_name

        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items",
            query_string=f"product_name={item_1_name}",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], item_1_name)

        wishlist2 = self._create_wishlists(1)[0]
        items_list2 = WishlistItemFactory.create_batch(2)
        items_list3 = WishlistItemFactory.create_batch(3)
        for item in items_list2:
            item.product_name = "dog"
            resp = self.client.post(
                f"{BASE_URL}/{wishlist2.id}/items", json=item.serialize()
            )
        for item in items_list3:
            resp = self.client.post(
                f"{BASE_URL}/{wishlist2.id}/items", json=item.serialize()
            )
        # search items by name "dog"
        resp = self.client.get(
            f"{BASE_URL}/{wishlist2.id}/items", query_string="product_name=dog"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["product_name"], "dog")
        self.assertEqual(data[1]["product_name"], "dog")

    ##############################################################################
    #  A C T I O N   R O U T E  U N P U B L I S H  T E S T   C A S E S   H E R E
    ##############################################################################

    def test_unpublish_wishlist(self):
        """It should unpublish a wishlist"""
        wishlist = WishlistFactory()
        wishlist.is_public = True
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        wishlist_id = wishlist.id

        resp = self.client.put(f"{BASE_URL}/{wishlist_id}/unpublish")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], wishlist_id)
        self.assertEqual(data["is_public"], False)

        # testing idempotency
        resp2 = self.client.put(f"{BASE_URL}/{wishlist_id}/unpublish")

        self.assertEqual(data, resp2.get_json())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unpublish_wishlist_for_non_existent_wishlist(self):
        """It should return 404 status code when unpublishing a wishlist that does not exist"""
        resp = self.client.put(f"{BASE_URL}/99999/unpublish")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

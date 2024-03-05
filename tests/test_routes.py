"""
Wishlist API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist
from .factories import WishlistFactory, WishListItemFactory

# cspell: ignore psycopg testdb

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

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
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

    def test_create_wishlist(self):
        """It should create a new wishlist"""

        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(
            new_wishlist["description"],
            wishlist.description,
            "Description does not match",
        )
        self.assertEqual(
            new_wishlist["username"], wishlist.username, "Username does not match"
        )
        self.assertEqual(
            new_wishlist["is_public"], wishlist.is_public, "IsPublic does not match"
        )

        self.assertEqual(
            new_wishlist["created_at"],
            wishlist.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "Created at date does not match",
        )

        self.assertEqual(
            new_wishlist["last_updated_at"],
            wishlist.last_updated_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "Last updated date does not match",
        )

        # TODO: Add more tests when Read Wishlist is implemented

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

    ######################################################################
    #  I T E M   T E S T   C A S E S   H E R E
    ######################################################################

    def test_add_item(self):
        """It should Add an item to a wishlist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishListItemFactory()
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

    def test_read_item(self):
        """It should read an item from wishlist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishListItemFactory()
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
        item = WishListItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        """Case 1 : Wishlist does not exist"""
        dummy_wishlist_id = -10
        resp = self.client.get(
            f"{BASE_URL}/{dummy_wishlist_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        """Case 2 : Item does not exist"""
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
        item = WishListItemFactory()
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

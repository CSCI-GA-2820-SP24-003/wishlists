"""
Wishlist API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist
from .factories import WishlistFactory

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
    #  P L A C E   T E S T   C A S E S   H E R E
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

    def _create_wishlists(self, count):
        """Factory method to wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return new_wishlist
